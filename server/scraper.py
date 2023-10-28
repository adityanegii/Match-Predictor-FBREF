import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from helpers.scraper_helpers import parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting
from constants import MATCH_FILE

HEADERS = [
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"},
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0"},
        {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"},
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"},
        {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"},
        {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36"},
        {"User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36"}
    ]

def parse_url(url, parse, text):
    while True:
        data = requests.get(url, headers=random.choice(HEADERS))
        if (data.status_code == 200):
            try:
                df = pd.read_html(data.text, match=text)[0]
                df = parse(df)
                return df
            except:
                time.sleep(10)
        else:
            print(f"Error: {data.status_code}")
            time.sleep(10)

def scrape(years, link):
    # parse_fcns = [parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting]
    parse_fcns = [parse_def, parse_gca, parse_misc, parse_pass, parse_poss, parse_shooting]
    # table_names = ["Defensive Actions", "Goal and Shot Creation", "Goalkeeping", "Miscellaneous Stats", "Passing", "Pass Types", "Possession", "Shooting"]
    table_names = ["Defensive Actions", "Goal and Shot Creation", "Miscellaneous Stats", "Passing", "Possession", "Shooting"]

    all_matches = []
    standings_url = link
    teams = {}

    for year in years:
        data = requests.get(standings_url)
        soup = BeautifulSoup(data.text, features="html.parser")
        standings_table = soup.select('table.stats_table')[0]

        links = [l.get("href") for l in standings_table.find_all('a') if '/squads/' in l.get("href")]

        if year == years[0]:
            teams = {x.split("/")[-1] for x in links}
            print(teams)

        team_urls = [f"https://fbref.com{l}" for l in links if l.split("/")[-1] in teams]

        previous_season = soup.select("a.prev")[0].get("href")
        standings_url = f"https://fbref.com{previous_season}"
        
        # Get team data

        for team_url in team_urls:
            # Get match data
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
            data = requests.get(team_url)
            time.sleep(3)

            print(team_name + " " + str(year))
            matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
            matches = matches.drop(columns=["Poss", "xG", "Attendance", "Captain", "Match Report", "Referee", "Notes"])
                
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
                time.sleep(random.randint(1, 3))
            
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
