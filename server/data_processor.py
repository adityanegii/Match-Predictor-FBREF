import pandas as pd
from constants import DATE, WINDOW

class MissingDict(dict):
    __missing__ = lambda self, key: key

def get_data(file):
    return pd.read_csv(file, index_col=0)

def clean_data(matches_df):
    # Create map to standardize team names
    map_values = {
        # Premier League
        "Brighton and Hove Albion": "Brighton",
        "Manchester United": "Manchester Utd", 
        "Newcastle United": "Newcastle Utd",
        "Tottenham Hotspur": "Tottenham",
        "West Ham United": "West Ham",
        "Nott'ham Forest": "Nottingham Forest",
        "Wolverhampton Wanderers": "Wolves",
        "Sheffield United": "Sheffield Utd",   
        # Ligue 1
        "Paris S-G" : "PSG",
        "Paris Saint Germain" : "PSG",
        "Saint Etienne": "Saint-Étienne",
        # Bundesliga
        "Gladbach": "Monchengladbach",
        "Köln": "FC Koln",
        "Koln": "FC Koln",
        "Leverkusen": "Bayer Leverkusen",
        "Eint Frankfurt": "Eintracht Frankfurt",
        "St. Pauli": "St Pauli",
        # Serie A
        "Internazionale": "Inter",
        # La Liga
        "Almeria": "Almería",
        "Atletico Madrid": "Atlético Madrid",
        "Cadiz": "Cádiz",
        "Betis": "Real Betis",
        "Alaves": "Alavés",
        "Leganes": "Leganés"
    }

    mapping = MissingDict(**map_values)

    # # Replace team names with standardized names
    matches_df['team'] = matches_df['team'].replace(mapping)
    matches_df['opponent'] = matches_df['opponent'].replace(mapping)

    # Split fixtures into past and future
    past_fixtures = matches_df[matches_df['date'].dt.date < pd.Timestamp(DATE).date()]
    next_fixtures = matches_df[matches_df['date'].dt.date >= pd.Timestamp(DATE).date()]

    # Sort the DataFrame by team and date
    next_fixtures = next_fixtures.sort_values(by=['team', 'date'])

    # Group by team and select the first fixture for each team
    first_fixtures = next_fixtures.groupby('team').first().reset_index()
    first_fixtures = first_fixtures.sort_values(by=['opponent', 'date'])
    unique_opponents = first_fixtures.drop_duplicates(subset='opponent', keep='first')

    # Get all past fixtures and the next fixture for each team
    matches_df = pd.concat([past_fixtures, unique_opponents])
    matches_df = matches_df.sort_values(by=['season', 'team', 'date'], ascending=[False, True, True])
    
    # Convert column data to numeric
    matches_df["date"] = pd.to_datetime(matches_df["date"])
    matches_df["day_code"] = matches_df["date"].dt.dayofweek
    matches_df["venue_code"] = matches_df["venue"].astype('category').cat.codes
    matches_df["team_code"] = matches_df["team"].astype('category').cat.codes
    matches_df["opp_code"] = matches_df["opponent"].astype('category').cat.codes
    matches_df["hour"] = matches_df["time"].str.replace(":.+", "", regex=True).astype("int")
    matches_df["pts"] = matches_df["result"].map({'W': 3, 'D': 1, 'L': 0})
    matches_df["gf"] = matches_df["gf"].astype("float64")
    matches_df["ga"] = matches_df["ga"].astype("float64")


    teams = matches_df['team'].unique().tolist()
    dfs = [matches_df[matches_df['team'] == x] for x in teams]
    dfs = [x.reset_index(drop=True) for x in dfs]

    valid_cols = matches_df.select_dtypes(include=['int8', 'int64', 'float64', 'int32']).columns.tolist()

    for df in dfs:
        rows = df.index
        for col in valid_cols:
            for i in rows[:-1]:
                value = df.at[i, col]
                if pd.isnull(value):
                    if i == 0:
                        average = df[col].dropna().mean()
                        df.at[i, col] = average 
                    else:
                        average = df[col][:i].dropna().mean()
                        df.at[i, col] = average

    return pd.concat(dfs).sort_values(by=['team', 'date']).reset_index(drop=True)

def get_overall_averages(final_matches):
    cols = list()
    with open("data/cols.txt", "r") as f:
        for line in f:
            cols.append(line.strip())

    final_matches[cols] = final_matches[cols].astype(float)
    
    rolling_averages = final_matches.groupby('team')[cols].rolling(window=WINDOW, min_periods=3, closed='left').mean()
    rolling_averages.reset_index(level=0, drop=True, inplace=True)

    overall_averages = final_matches.groupby('team')[cols].apply(lambda x: x.shift().expanding().mean())
    overall_averages.reset_index(level=0, drop=True, inplace=True)
    return pd.concat([final_matches, rolling_averages.add_suffix('_rolling'), overall_averages.add_suffix('_mean')], axis=1)

def combine(df):
    home_table = df[df["venue"] == "Home"].sort_values(by=['date', 'time', 'team'])
    away_table = df[df["venue"] == "Away"].sort_values(by=['date', 'time', 'opponent'])
    home_table_renamed = home_table.rename(columns={"team": "home_team", "opponent": "away_team", "gf": "gf_home", "ga": "gf_away"})
    away_table_renamed = away_table.rename(columns={"team": "away_team", "opponent": "home_team", "gf": "gf_away", "ga": "gf_home"})

    merged_df = pd.merge(home_table_renamed, away_table_renamed, on=["date", "comp", "round", "day", "season", "round", "time", "home_team", "away_team", "gf_home", "gf_away"], suffixes=("_home", "_away"))
    merged_df['result_code'] = (
        merged_df['gf_home'] > merged_df['gf_away']).astype(int) - (
        merged_df['gf_home'] < merged_df['gf_away']).astype(int) + 1 # 2 for home team win, 1 for draw, 0 for away team win

    return merged_df

def mark_promoted(df):
    # df["date"] = pd.to_datetime(df["date"]) # can remove this later

    # df["year"] = df["date"].dt.year

    # df["season"] = pd.to_datetime(df["season"])

    teams_per_year = df.groupby("season")["home_team"].unique()
    first_year = df["season"].min()

    filtered_df = df[df["season"] != first_year]
    
    filtered_df["promoted_home"] = 0
    filtered_df["promoted_away"] = 0

    for year, teams in teams_per_year.items():
        if year == first_year:
            continue
        prev_year = str(int(year) - 1)
        prev_teams = teams_per_year[prev_year]
        promoted_teams = [x for x in teams if x not in prev_teams]


        for team in promoted_teams:
            filtered_df.loc[(filtered_df["season"] == year) & (filtered_df["home_team"] == team), "promoted_home"] = 1
            filtered_df.loc[(filtered_df["season"] == year) & (filtered_df["away_team"] == team), "promoted_away"] = 1

    return filtered_df