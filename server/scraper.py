import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from helpers.scraper_helpers import parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting
from constants import MATCH_FILE, HEADERS
from fake_useragent import UserAgent

def get_request(url, headers=HEADERS):
    data = requests.get(url, headers)
    time.sleep(6)
    while data.status_code != 200:
        print(data.status_code, url)
        time.sleep(600)
        data = requests.get(url, headers)
    return data

def parse_url(url: str, parse, text: str):
    data = get_request(url)
    df = pd.read_html(data.text, match=text)[0]
    df = parse(df)
    return df

def scrape(years: list, link: str):
    ua = UserAgent()
    HEADERS["User-Agent"] = ua.random

    # parse_fcns = [parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting]
    parse_fcns = [parse_def, parse_gca, parse_misc, parse_pass, parse_poss, parse_shooting]
    # table_names = ["Defensive Actions", "Goal and Shot Creation", "Goalkeeping", "Miscellaneous Stats", "Passing", "Pass Types", "Possession", "Shooting"]
    table_names = ["Defensive Actions", "Goal and Shot Creation", "Miscellaneous Stats", "Passing", "Possession", "Shooting"]

    all_matches = []
    standings_url = link
    teams = {}
    try:
        for year in years:
            data = get_request(standings_url)

            soup = BeautifulSoup(data.text, features="html.parser")
            standings_table = soup.select('table.stats_table')[0]

            links = [l.get("href") for l in standings_table.find_all('a') if '/squads/' in l.get("href")]

            teams = {x.split("/")[-1] for x in links}

            team_urls = [f"https://fbref.com{l}" for l in links if l.split("/")[-1] in teams]

            previous_season = soup.select("a.prev")[0].get("href")
            standings_url = f"https://fbref.com{previous_season}"
            
            
            # Get team data
            for team_url in team_urls:
                HEADERS["User-Agent"] = ua.random
                # Get match data
                team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
                data = get_request(team_url)

                print(team_name + " " + str(year))
                matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
                matches = matches.drop(columns=["Poss", "xG", "Attendance", "Captain", "Referee", "Notes"])
                    
                # Get stats links
                soup = BeautifulSoup(data.text, features="html.parser")
                links = [l.get("href") for l in soup.find_all('a')]
                links = [l for l in links if l and ("all_comps/shooting/" in l or "all_comps/passing/" in l
                                                    or "all_comps/gca/" in l or "all_comps/defense/" in l
                                                    or "all_comps/possession/" in l or "all_comps/misc/" in l)]
                links = list(set(links))
                links = [f"https://fbref.com{l}" for l in links]
                links.sort()
                    
                dfs = []
                for url, category, parser in zip(links, table_names, parse_fcns):
                    dfs.append(parse_url(url, parser, category))
                
                team_data = matches
                for df in dfs:
                    try:
                        team_data = team_data.merge(df, how="left", on="Date")
                    except ValueError:
                        continue
            
                team_data = team_data[(team_data["Comp"] == "Premier League")
                                    | (team_data["Comp"] == "Bundesliga")
                                    | (team_data["Comp"] == "La Liga")
                                    | (team_data["Comp"] == "Serie A")
                                    | (team_data["Comp"] == "Ligue 1")
                                    ]
                
                # Add year and team name
                team_data["Season"] = year
                team_data["Team"] = team_name
                all_matches.append(team_data)
    except Exception as e:
        print(e)
        print("Error with", team_name)
        print("Links", links)
        print("Team URLs", team_urls)
        print("Team Name", team_name)
        print("Year", year)
        print("Previous Season", previous_season)
        print("Standings URL", standings_url)
        print("Teams", teams)
    
    matches_df = pd.concat(all_matches)
    matches_df.columns = [c.lower() for c in matches_df.columns]

    matches_df["date"] = pd.to_datetime(matches_df["date"])

    matches_df[matches_df["comp"] == "Premier League"].to_csv("data/matches_ENG1.csv", index = False)
    matches_df[matches_df["comp"] == "Bundesliga"].to_csv("data/matches_GER1.csv", index = False)
    matches_df[matches_df["comp"] == "La Liga"].to_csv("data/matches_SPA1.csv", index = False)
    matches_df[matches_df["comp"] == "Serie A"].to_csv("data/matches_ITA1.csv", index = False)
    matches_df[matches_df["comp"] == "Ligue 1"].to_csv("data/matches_FRA1.csv", index = False)
    matches_df.to_csv(MATCH_FILE, index=False)
    return matches_df