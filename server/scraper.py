import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

from typing import Callable

from helpers.scraper_helpers import parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting
from constants import MATCH_FILE, HEADERS, current_year, CHROMEDRIVER_PATH
from fake_useragent import UserAgent
from data_models.RawMatch import RawMatch
from sqlalchemy import insert, update, bindparam
from sqlalchemy.orm import sessionmaker

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def open_chromedriver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3 ") # Suppress logs
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def close_chromedriver(driver: webdriver.Chrome):
    driver.quit()

# DEPRECATED BECAUSE OF NEED OF SELENIUM
# def get_request(url: str, headers=HEADERS) -> str:
#     data = requests.get(url, headers)
#     time.sleep(6)
#     while data.status_code != 200:
#         print(data.status_code, url)
#         time.sleep(600)
#         data = requests.get(url, headers)
#     return data.text


# Function that returns HTML contrent as string
def get_request(url: str, driver: webdriver.Chrome, wait_selector: str = "body", timeout: int = 20, delay: int = 6) -> str:
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
    )
    time.sleep(delay)
    return driver.page_source

def parse_url(url: str, parse: Callable, text: str, driver: webdriver.Chrome) -> pd.DataFrame:
    while True:
        try:
            data = get_request(url, driver=driver)
            tables = pd.read_html(data, match=text)
            df = tables[0]
            df = parse(df)
            return df
        except ValueError:
            print("Retrying to parse", url)
            time.sleep(10)
        

def scrape(link: str, session: sessionmaker) -> pd.DataFrame:
    ua = UserAgent()
    HEADERS["User-Agent"] = ua.random

    parse_fcns = [parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting]
    table_names = ["Defensive Actions", "Goal and Shot Creation", "Goalkeeping", "Miscellaneous Stats", "Passing", "Pass Types", "Possession", "Shooting"]

    all_matches = []
    standings_url = link
    teams = {}

    # Check for existing data
    seasons = get_existing_seasons(session)

    if not seasons:
        years = list(range(current_year, current_year - 4, - 1))
    else:
        years = [current_year]

    try:
        # Open ChromeDriver
        driver = open_chromedriver()

        for year in years:
            data = get_request(standings_url, driver=driver)

            # soup = BeautifulSoup(data.text, features="html.parser")
            soup = BeautifulSoup(data, features="html.parser")
            standings_table = soup.select('table.stats_table')[0]

            # Find all team links
            links = [l.get("href") for l in standings_table.find_all('a') if '/squads/' in l.get("href")]
            
            teams = {x.split("/")[-1] for x in links}

            team_urls = [f"https://fbref.com{l}" for l in links if l.split("/")[-1] in teams]

            # Get previous year's table
            previous_season = soup.select("a.prev")[0].get("href")
            standings_url = f"https://fbref.com{previous_season}"
            
            
            # Get team data
            for team_url in team_urls:
                HEADERS["User-Agent"] = ua.random
                # Get match data
                team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
                data = get_request(team_url, driver=driver)

                print(team_name + " " + str(year))
                # matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
                matches = pd.read_html(data, match="Scores & Fixtures")[0]

                if "xG" in matches.columns:
                    matches = matches.drop(columns=["Poss", "xG", "Attendance", "Captain", "Referee", "Notes"])
                else:
                    matches = matches.drop(columns=["Poss", "Attendance", "Captain", "Referee", "Notes"])
                    matches["xGA"] = -1.0

                # Get stats links
                # soup = BeautifulSoup(data.text, features="html.parser")
                soup = BeautifulSoup(data, features="html.parser")

                # Get links for stats tables
                links = [l.get("href") for l in soup.find_all('a')]
                links = [l for l in links if l and ("all_comps/shooting/" in l or "all_comps/passing/" in l or "all_comps/keeper" in l
                                                    or "all_comps/gca/" in l or "all_comps/defense/" in l or "all_comps/passing_types" in l
                                                    or "all_comps/possession/" in l or "all_comps/misc/" in l)]
                links = list(set(links))
                links = [f"https://fbref.com{l}" for l in links]
                links.sort()
                    
                # Parse categories
                dfs = []
                for url, category, parser in zip(links, table_names, parse_fcns):
                    dfs.append(parse_url(url, parser, category, driver))
                
                # Merge all category dfs into one big df
                team_data = matches[matches["Date"] != "Date"].dropna(subset=["Date"])
                for df in dfs:
                    try:
                        t_df = df.dropna(subset=["Date"])
                        t_df = t_df[t_df["Date"] != "Date"]
                        team_data = team_data.merge(t_df, how="left", on="Date")
                    except ValueError:
                        continue

                # Calculate days since last match
                team_data["Days Since Last Game"] = (pd.to_datetime(team_data["Date"]) - pd.to_datetime(team_data["Date"].shift())).dt.days
                team_data["Days Since Last Game"].fillna(90, inplace=True)
                team_data["Is First Game"] = team_data["Days Since Last Game"] == 90

                # Keep only league matches
                team_data = team_data[(team_data["Comp"] == "Premier League")
                                    | (team_data["Comp"] == "Bundesliga")
                                    | (team_data["Comp"] == "La Liga")
                                    | (team_data["Comp"] == "Serie A")
                                    | (team_data["Comp"] == "Ligue 1")
                                    ]
                
                # Add year and team name
                team_data["Season"] = str(year)
                team_data["Team"] = team_name
                all_matches.append(team_data)
            #     break
            # break
            
    except Exception as e:
        print(e)
        print("Current url:", url)
        print("Current category:", category)
        print("Error with", team_name)
        print("Year", year)
        print("Previous Season", previous_season)
        print("Standings URL", standings_url)
    finally:
        # Close ChromeDriver
        close_chromedriver(driver)

    matches_df = pd.concat(all_matches)
    matches_df.columns = [c.lower() for c in matches_df.columns]

    matches_df["date"] = pd.to_datetime(matches_df["date"])

    matches_df = clean_columns(matches_df)

    # Convert to csv
    matches_df[matches_df["comp"] == "Premier League"].to_csv("data/raw/matches_ENG1.csv", index = False)
    matches_df[matches_df["comp"] == "Bundesliga"].to_csv("data/raw/matches_GER1.csv", index = False)
    matches_df[matches_df["comp"] == "La Liga"].to_csv("data/raw/matches_SPA1.csv", index = False)
    matches_df[matches_df["comp"] == "Serie A"].to_csv("data/raw/matches_ITA1.csv", index = False)
    matches_df[matches_df["comp"] == "Ligue 1"].to_csv("data/raw/matches_FRA1.csv", index = False)
    matches_df.to_csv(MATCH_FILE, index=False)

    # Save df to database
    print(years)

    records = matches_df.to_dict(orient="records")

    if len(years) == 1:
        print("updating")
        stmt = (
            update(RawMatch)
            .where(
                RawMatch.date == bindparam("date"),
                RawMatch.team == bindparam("team")
            )
            .values({col: bindparam(col) for col in matches_df.columns})
            .execution_options(synchronize_session=False)
        )
        session.execute(stmt, records)  # stmt first, params second
    else:
        print("inserting")
        stmt = insert(RawMatch)
        session.execute(stmt, records)  # stmt first, params second
    session.commit()

    return matches_df

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Clean column names by applying a series of transformations.
    '''
    def clean_name(col: str) -> str:
        col = col.lower().strip()
        col = col.replace(" ", "_")
        col = col.rstrip("_")
        return col
    
    df.columns = [clean_name(col) for col in df.columns]

    return df

def get_existing_seasons(session: object) -> bool:
    existing_seasons = session.query(RawMatch.season).distinct().all()  # Get all distinct seasons

    if existing_seasons:
        return True
    else:
        return False