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
            home_rolling_averages.add_suffix('_atHome_rolling'), 
            away_rolling_averages.add_suffix('_atAway_rolling'), 
            home_overall_averages.add_suffix('_atHome_mean'), 
            away_overall_averages.add_suffix('_atAway_mean')
        ], 
        axis=1
    )

    # Handle NaN values
    # Rule 1: drop rows where ALL averages (home + away + general) are NaN
    mask_all_nan = df.filter(like="_atHome_").isna().all(axis=1) & df.filter(like="_atAway_").isna().all(axis=1)
    df = df[~mask_all_nan]

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
    szn_cum_cols = pd.DataFrame({
        "szn_cum_games": group.cumcount().replace(0, np.nan),
        "szn_cum_wins": group["win"].cumsum().shift(1, fill_value=0),
        "szn_cum_draws": group["draw"].cumsum().shift(1, fill_value=0),
        "szn_cum_losses": group["loss"].cumsum().shift(1, fill_value=0),
        "szn_cum_pts": group["pts"].cumsum().shift(1, fill_value=0),
    })

    # Get rolling stats (past 5 games)
    szn_last_5_cols = pd.DataFrame()
    szn_last_5_cols['szn_wins_last5'] = group['win'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    szn_last_5_cols['szn_draws_last5'] = group['draw'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    szn_last_5_cols['szn_losses_last5'] = group['loss'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    szn_last_5_cols['szn_pts_last5'] = group['pts'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    
    home_df = df[df["venue"] == "Home"]
    away_df = df[df["venue"] == "Away"]

    # Calculate home cumulative counts and sums
    home_group = home_df.groupby(["season", "team"])
    home_szn_cum_cols = pd.DataFrame({
        "szn_cum_games_atHome": home_group.cumcount().replace(0, np.nan),
        "szn_cum_wins_atHome": home_group["win"].cumsum().shift(1, fill_value=0),
        "szn_cum_draws_atHome": home_group["draw"].cumsum().shift(1, fill_value=0),
        "szn_cum_losses_atHome": home_group["loss"].cumsum().shift(1, fill_value=0),
        "szn_cum_pts_atHome": home_group["pts"].cumsum().shift(1, fill_value=0),
    })

    # Get rolling stats (past 5 home games)
    home_szn_last_5_cols = pd.DataFrame()
    home_szn_last_5_cols['szn_wins_atHome_last5'] = home_group['win'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    home_szn_last_5_cols['szn_draws_atHome_last5'] = home_group['draw'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    home_szn_last_5_cols['szn_losses_atHome_last5'] = home_group['loss'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    home_szn_last_5_cols['szn_pts_atHome_last5'] = home_group['pts'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)

    # Calculate away cumulative counts and sums
    away_group = away_df.groupby(["season", "team"])
    away_szn_cum_cols = pd.DataFrame({
        "szn_cum_games_atAway": away_group.cumcount().replace(0, np.nan),
        "szn_cum_wins_atAway": away_group["win"].cumsum().shift(1, fill_value=0),
        "szn_cum_draws_atAway": away_group["draw"].cumsum().shift(1, fill_value=0),
        "szn_cum_losses_atAway": away_group["loss"].cumsum().shift(1, fill_value=0),
        "szn_cum_pts_atAway": away_group["pts"].cumsum().shift(1, fill_value=0),
    })

    # Get rolling stats (past 5 away games)
    away_szn_last_5_cols = pd.DataFrame()
    away_szn_last_5_cols['szn_wins_atAway_last5'] = away_group['win'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    away_szn_last_5_cols['szn_draws_atAway_last5'] = away_group['draw'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    away_szn_last_5_cols['szn_losses_atAway_last5'] = away_group['loss'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)
    away_szn_last_5_cols['szn_pts_atAway_last5'] = away_group['pts'].rolling(window=WINDOW, min_periods=1, closed='left').mean().shift(1, fill_value=0).reset_index(level=0, drop=True)

    # Combine all cumulative columns
    df = pd.concat([df, szn_cum_cols], axis=1)
    df = pd.concat([df, home_szn_cum_cols], axis=1)
    df = pd.concat([df, away_szn_cum_cols], axis=1)

    # df = pd.concat([df, szn_last_5_cols], axis=1)
    # df = pd.concat([df, home_szn_last_5_cols], axis=1)
    # df = pd.concat([df, away_szn_last_5_cols], axis=1)

    # Reset first match of each season for each team to 0
    first_rows = df.groupby(["season", "team"]).head(1).index
    df.loc[first_rows, ["szn_cum_games", "szn_cum_wins", "szn_cum_draws", "szn_cum_losses", "szn_cum_pts", 
                        "szn_cum_games_atHome", "szn_cum_wins_atHome", "szn_cum_draws_atHome", "szn_cum_losses_atHome", "szn_cum_pts_atHome", 
                        "szn_cum_games_atAway", "szn_cum_wins_atAway", "szn_cum_draws_atAway", "szn_cum_losses_atAway", "szn_cum_pts_atAway",
                        ]] = 0
    
    # make rows for szn_cum_pts_atHome_forAwayTeam and szn_cum_pts_atAway_forHomeTeam equal to 0 for all values
    df.loc[df["venue"] == "Home", "szn_cum_pts_atAway"] = 0
    df.loc[df["venue"] == "Away", "szn_cum_pts_atHome"] = 0

    # Calculate percentages
    pct_cols = pd.DataFrame({
        "szn_win_pct": df["szn_cum_wins"] / df["szn_cum_games"],
        "szn_draw_pct": df["szn_cum_draws"] / df["szn_cum_games"],
        "szn_loss_pct": df["szn_cum_losses"] / df["szn_cum_games"],

        "szn_win_pct_atHome": df["szn_cum_wins_atHome"] / df["szn_cum_games_atHome"],
        "szn_draw_pct_atHome": df["szn_cum_draws_atHome"] / df["szn_cum_games_atHome"],
        "szn_loss_pct_atHome": df["szn_cum_losses_atHome"] / df["szn_cum_games_atHome"],
        
        "szn_win_pct_atAway": df["szn_cum_wins_atAway"] / df["szn_cum_games_atAway"],
        "szn_draw_pct_atAway": df["szn_cum_draws_atAway"] / df["szn_cum_games_atAway"],
        "szn_loss_pct_atAway": df["szn_cum_losses_atAway"] / df["szn_cum_games_atAway"],

        "szn_pts_per_game": df["szn_cum_pts"] / df["szn_cum_games"],
        "szn_pts_per_game_atHome": df["szn_cum_pts_atHome"] / df["szn_cum_games_atHome"],
        "szn_pts_per_game_atAway": df["szn_cum_pts_atAway"] / df["szn_cum_games_atAway"],
    })

    pct_cols = pct_cols.fillna(0)

    df = pd.concat([df, pct_cols], axis=1)
    # df = pd.concat([df, pct_cols, rolling_cols], axis=1)
    
    df.to_csv("data/processed/temp.csv")
    # Drop temporary columns
    df.drop(columns=["win", "draw", "loss", 
                    "szn_cum_games", "szn_cum_wins", "szn_cum_draws", "szn_cum_losses",
                    "szn_cum_games_atHome", "szn_cum_wins_atHome", "szn_cum_draws_atHome", "szn_cum_losses_atHome",
                    "szn_cum_games_atAway", "szn_cum_wins_atAway", "szn_cum_draws_atAway", "szn_cum_losses_atAway"], inplace=True)

    return df

def combine(df:pd.DataFrame) -> pd.DataFrame:
    home_table = df[df["venue"] == "Home"].sort_values(by=['date', 'time', 'team'])
    away_table = df[df["venue"] == "Away"].sort_values(by=['date', 'time', 'opponent'])
    home_table_renamed = home_table.rename(columns={"team": "home_team", "opponent": "away_team", "gf": "gf_forHomeTeam", "ga": "gf_forAwayTeam"})
    away_table_renamed = away_table.rename(columns={"team": "away_team", "opponent": "home_team", "gf": "gf_forAwayTeam", "ga": "gf_forHomeTeam"})

    merged_df = pd.merge(home_table_renamed, away_table_renamed, on=["date", "comp", "round", "day", "season", "round", "time", "home_team", "away_team", "gf_forHomeTeam", "gf_forAwayTeam"], suffixes=("_forHomeTeam", "_forAwayTeam"))
    merged_df['result_code'] = (
        merged_df['gf_forHomeTeam'] > merged_df['gf_forAwayTeam']).astype(int) - (
        merged_df['gf_forHomeTeam'] < merged_df['gf_forAwayTeam']).astype(int) + 1 # 2 for home team win, 1 for draw, 0 for away team win
    

    return merged_df

def mark_promoted(df:pd.DataFrame) -> pd.DataFrame:
    teams_per_year = df.groupby("season")["home_team"].unique()
    first_year = df["season"].min()

    filtered_df = df.loc[df["season"] != first_year].copy()
        
    # Create new columns for promoted teams
    filtered_df.loc[:,"promoted_forHomeTeam"] = 0
    filtered_df.loc[:,"promoted_forAwayTeam"] = 0

    for year, teams in teams_per_year.items():
        if year == first_year:
            continue
        prev_year = str(int(year) - 1)
        prev_teams = teams_per_year[prev_year]
        promoted_teams = [x for x in teams if x not in prev_teams]


        for team in promoted_teams:
            filtered_df.loc[(filtered_df["season"] == year) & (filtered_df["home_team"] == team), "promoted_forHomeTeam"] = 1
            filtered_df.loc[(filtered_df["season"] == year) & (filtered_df["away_team"] == team), "promoted_forAwayTeam"] = 1

    return filtered_df