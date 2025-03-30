DATE = 'today'
WINDOW = 5
# DATE = '26-10-2023'
TEST_DATE = '25-10-2023'
MATCH_FILE = 'data/raw/matches.csv'
CLEAN_DATA = 'data/processed/clean_data.csv'

league_id = {
    'La Liga': 12,
    'Bundesliga': 20,
    'Serie A': 11,
    'Ligue 1': 13,
    'Premier League': 9
}

league_full = {
    'ENG1': 'Premier League',
    'ESP1': 'La Liga',
    'GER1': 'Bundesliga',
    'ITA1': 'Serie A',
    'FRA1': 'Ligue 1'
}

HEADERS = {
    "User-Agent": None,
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fbref.com/en",
}

DATABASE_URL = "sqlite:///data/FBREF_matches.sqlite"

current_year = 2024