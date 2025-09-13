import pandas as pd
import numpy as np
from constants import DATE, WINDOW

class MissingDict(dict):
    __missing__ = lambda self, key: key

def get_data(file):
    return pd.read_csv(file, index_col=0)

def clean_data(matches_df:pd.DataFrame) -> pd.DataFrame:
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

    # Correctly calculate xga if xga is -1.0 (find corresponding game for other team and look at their xg)
    opp_xg_lookup = (
        matches_df.set_index(['team', 'opponent', 'date'])['xg']
        .to_dict()
    )

    for idx, row in matches_df.iterrows():
        if row['xga'] == -1.0:
            opp_xg = opp_xg_lookup.get((row['opponent'], row['team'], row['date']), np.nan)
            matches_df.at[idx, 'xga'] = opp_xg if pd.notnull(opp_xg) else np.nan


    # teams = matches_df['team'].unique().tolist()
    # dfs = [matches_df[matches_df['team'] == x] for x in teams]
    # dfs = [x.reset_index(drop=True) for x in dfs]

    # valid_cols = matches_df.select_dtypes(include=['int8', 'int64', 'float64', 'int32']).columns.tolist()

    # for df in dfs:
    #     rows = df.index
    #     for col in valid_cols:
    #         for i in rows[:-1]:
    #             value = df.at[i, col]
    #             if pd.isnull(value):
    #                 if i == 0:
    #                     average = df[col].dropna().mean()
    #                     df.at[i, col] = average 
    #                 else:
    #                     average = df[col][:i].dropna().mean()
    #                     df.at[i, col] = average

    # return pd.concat(dfs).sort_values(by=['team', 'date']).reset_index(drop=True)

    numeric_cols = matches_df.select_dtypes(include=['int8','int64','float64','int32']).columns

    def fill_team(df):
        df = df.sort_values('date')
        rolling_avg = df[numeric_cols].expanding().mean().shift()
        team_mean = df[numeric_cols].mean()
        df[numeric_cols] = df[numeric_cols].fillna(rolling_avg).fillna(team_mean)
        return df

    matches_df = (
        matches_df.groupby('team', group_keys=False)
        .apply(fill_team)
        .sort_values(['team', 'date'])
        .reset_index(drop=True)
    )

    return matches_df

def get_averages(final_matches: pd.DataFrame) -> pd.DataFrame:
    cols = list()
    with open("data/cols.txt", "r") as f:
        for line in f:
            cols.append(line.strip())

    final_matches[cols] = final_matches[cols].astype(float)
    
    # Base averages
    rolling_averages = final_matches.groupby('team')[cols].rolling(window=WINDOW, min_periods=3, closed='left').mean().reset_index(level=0, drop=True)
    overall_averages = final_matches.groupby('team')[cols].apply(lambda x: x.shift().expanding().mean()).reset_index(level=0, drop=True)

    # Home and Away averages
    home_rolling_averages = final_matches[final_matches["venue"] == "Home"].groupby('team')[cols].rolling(window=WINDOW, min_periods=3, closed='left').mean().reset_index(level=0, drop=True)
    away_rolling_averages = final_matches[final_matches["venue"] == "Away"].groupby('team')[cols].rolling(window=WINDOW, min_periods=3, closed='left').mean().reset_index(level=0, drop=True)

    home_overall_averages = final_matches[final_matches["venue"] == "Home"].groupby('team')[cols].apply(lambda x: x.shift().expanding().mean()).reset_index(level=0, drop=True)
    away_overall_averages = final_matches[final_matches["venue"] == "Away"].groupby('team')[cols].apply(lambda x: x.shift().expanding().mean()).reset_index(level=0, drop=True)

    df = pd.concat(
        [
            final_matches, rolling_averages.add_suffix('_rolling'),
            overall_averages.add_suffix('_mean'), 
            home_rolling_averages.add_suffix('_home_rolling'), 
            away_rolling_averages.add_suffix('_away_rolling'), 
            home_overall_averages.add_suffix('_home_mean'), 
            away_overall_averages.add_suffix('_away_mean')
        ], 
        axis=1
    )

    # Handle NaN values
    # Rule 1: drop rows where ALL averages (home + away + general) are NaN
    mask_all_nan = df.filter(like="_home_").isna().all(axis=1) & df.filter(like="_away_").isna().all(axis=1)
    df = df[~mask_all_nan]

    # Get number of nan values:
    num_nans = df.isna().sum().sum()

    # Rule 2: replace "structural" NaNs with 0 (e.g. away stats in home games)
    df = df.fillna(0)

    return df.reset_index(drop=True)

def calculate_team_results_and_points(df:pd.DataFrame) -> pd.DataFrame:

    # Reference DF
    results = pd.DataFrame({
    "win": (df["pts"] == 3).astype(int),
    "draw": (df["pts"] == 1).astype(int),
    "loss": (df["pts"] == 0).astype(int)
    })
    df = pd.concat([df, results], axis=1)

    group = df.groupby(["season", "team"])

    # Calculate cumulative counts and sums
    cum_cols = pd.DataFrame({
        "cum_games": group.cumcount().replace(0, np.nan),
        "cum_wins": group["win"].cumsum().shift(1, fill_value=0),
        "cum_draws": group["draw"].cumsum().shift(1, fill_value=0),
        "cum_losses": group["loss"].cumsum().shift(1, fill_value=0),
        "cum_pts": group["pts"].cumsum().shift(1, fill_value=0)
    })
    
    df = pd.concat([df, cum_cols], axis=1)

    # Reset first match of each season for each team to 0
    first_rows = df.groupby(["season", "team"]).head(1).index
    df.loc[first_rows, ["cum_games", "cum_wins", "cum_draws", "cum_losses", "cum_pts"]] = 0

    # Calculate percentages
    pct_cols = pd.DataFrame({
        "win_pct": df["cum_wins"] / df["cum_games"],
        "draw_pct": df["cum_draws"] / df["cum_games"],
        "loss_pct": df["cum_losses"] / df["cum_games"]
    })

    df = pd.concat([df, pct_cols], axis=1)
    
    # Drop temporary columns
    df.drop(columns=["win", "draw", "loss", "cum_games", "cum_wins", "cum_draws", "cum_losses"], inplace=True)

    df.to_csv("data/processed/temp.csv", index=False)  ### TO REMOVE
    return df

def combine(df:pd.DataFrame) -> pd.DataFrame:
    home_table = df[df["venue"] == "Home"].sort_values(by=['date', 'time', 'team'])
    away_table = df[df["venue"] == "Away"].sort_values(by=['date', 'time', 'opponent'])
    home_table_renamed = home_table.rename(columns={"team": "home_team", "opponent": "away_team", "gf": "gf_home", "ga": "gf_away"})
    away_table_renamed = away_table.rename(columns={"team": "away_team", "opponent": "home_team", "gf": "gf_away", "ga": "gf_home"})

    merged_df = pd.merge(home_table_renamed, away_table_renamed, on=["date", "comp", "round", "day", "season", "round", "time", "home_team", "away_team", "gf_home", "gf_away"], suffixes=("_home", "_away"))
    merged_df['result_code'] = (
        merged_df['gf_home'] > merged_df['gf_away']).astype(int) - (
        merged_df['gf_home'] < merged_df['gf_away']).astype(int) + 1 # 2 for home team win, 1 for draw, 0 for away team win
    

    return merged_df

def mark_promoted(df:pd.DataFrame) -> pd.DataFrame:
    teams_per_year = df.groupby("season")["home_team"].unique()
    first_year = df["season"].min()

    filtered_df = df.loc[df["season"] != first_year].copy()
        
    # Create new columns for promoted teams
    filtered_df.loc[:,"promoted_home"] = 0
    filtered_df.loc[:,"promoted_away"] = 0
    
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