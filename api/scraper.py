import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from scraper_helpers import parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting

def parse_url(url, parse, text, header):
    data = requests.get(url, headers=header)
    if (data.status_code != 200):
        print(f"Error: {data.status_code}")
    df = pd.read_html(data.text, match=text)[0]
    df = parse(df)
    return df

def scrape(years, link):
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
        {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"}
    ]
    parse_fcns = [parse_def, parse_gca, parse_gk, parse_misc, parse_pass, parse_passTypes, parse_poss, parse_shooting]
    table_names = ["Defensive Actions", "Goal and Shot Creation", "Goalkeeping", "Miscellaneous Stats", "Passing", "Pass Types", "Possession", "Shooting"]

    all_matches = []
    standings_url = link

    for year in years:
        data = requests.get(standings_url)
        soup = BeautifulSoup(data.text, features="html.parser")
        standings_table = soup.select('table.stats_table')[0]

        links = [l.get("href") for l in standings_table.find_all('a')]
        links = [l for l in links if '/squads/' in l]
        team_urls = [f"https://fbref.com{l}" for l in links]

        previous_season = soup.select("a.prev")[0].get("href")
        standings_url = f"https://fbref.com{previous_season}"
        
        # Get team data

        for team_url in team_urls:
            # Get match data
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
            data = requests.get(team_url)
            time.sleep(10)

            matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
            matches = matches.drop(columns=["Poss", "xG", "Attendance", "Captain", "Match Report", "Referee", "Notes"])
                
            # Get stats links
            soup = BeautifulSoup(data.text, features="html.parser")
            links = [l.get("href") for l in soup.find_all('a')]
            links = [l for l in links if l and ("all_comps/shooting" in l or "all_comps/keeper" in l or "all_comps/passing" in l
                                        or "all_comps/passing_types" in l or "all_comps/gca" in l or "all_comps/defense" in l
                                        or "all_comps/possession" in l or "all_comps/misc" in l)]
            links = list(set(links))
            links = [f"https://fbref.com{l}" for l in links]
            links.sort()
                
            dfs = []
            for url, category, parser in zip(links, table_names, parse_fcns):
                dfs.append(parse_url(url, parser, category, random.choice(HEADERS)))
                time.sleep(3)
            
            team_data = matches
            for df in dfs:
                try:
                    team_data = team_data.merge(df, how="left", on="Date")
                except ValueError:
                    continue

            team_data = team_data[team_data["Comp"] == "Premier League"]
            
            # Add year and team name
            team_data["Season"] = year
            team_data["Team"] = team_name
            all_matches.append(team_data)
    len(all_matches)
    matches_df = pd.concat(all_matches)
    matches_df.columns = [c.lower() for c in matches_df.columns]
    matches_df.to_csv("data/matches.csv")
    return matches_df
