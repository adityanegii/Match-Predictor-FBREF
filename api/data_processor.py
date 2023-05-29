import pandas as pd

class MissingDict(dict):
    __missing__ = lambda self, key: key

def get_data(file):
    return pd.read_csv(file, index_col=0)

def clean_data(matches_df):
    # Create map to standardize team names
    map_values = {
        "Brighton and Hove Albion": "Brighton",
        "Manchester United": "Manchester Utd", 
        "Newcastle United": "Newcastle Utd",
        "Tottenham Hotspur": "Tottenham",
        "West Ham United": "West Ham",
        "Nott'ham Forest": "Nottingham Forest",
        "Wolverhampton Wanderers": "Wolves",
    }

    mapping = MissingDict(**map_values)

    matches_df['team'] = matches_df['team'].replace(mapping)
    matches_df['opponent'] = matches_df['opponent'].replace(mapping)

    # Convert column data to numeric
    matches_df["date"] = pd.to_datetime(matches_df["date"])
    matches_df["day_code"] = matches_df["date"].dt.dayofweek
    matches_df["venue_code"] = matches_df["venue"].astype('category').cat.codes
    matches_df["team_code"] = matches_df["team"].astype('category').cat.codes
    matches_df["opp_code"] = matches_df["opponent"].astype('category').cat.codes
    matches_df["hour"] = matches_df["time"].str.replace(":.+", "", regex=True).astype("int")
    matches_df["pts"] = matches_df["result"].map({'W': 3, 'D': 1, 'L': 0})

    # Get only the matches that have been played + the next match for each team

    # Group the DataFrame by 'team' column
    grouped = matches_df.groupby('team')

    # Initialize an empty DataFrame to store the filtered matches
    all_matches = []

    # Iterate over each group
    for team, group in grouped:
        # Find the index of the next match for the team
        # next_match_index = group[group['date'].dt.date < pd.Timestamp.now().date()].shape[0]
        next_match_index = group[group['date'].dt.date < pd.to_datetime("2023-05-27").dt.date].shape[0]
        if (next_match_index <= group.shape[0]):
            all_matches.append(group[:next_match_index + 1])

    all_matches_df = pd.concat(all_matches).sort_values(by=['team', 'date'])

    # next_matches = all_matches_df[all_matches_df['date'].dt.date >= pd.Timestamp.now().date()].copy()
    next_matches = all_matches_df[all_matches_df['date'].dt.date >= pd.to_datetime("2023-05-27").dt.date].copy()
    next_matches['match'] = next_matches[['team', 'opponent']].apply(lambda x: '_'.join(sorted(x)), axis=1)
    groups = next_matches.groupby(['date', 'time', 'match'])
    valid_matches = groups.filter(lambda x: len(x) == 2)
    valid_matches.drop(columns=['match'], inplace=True)

    # final_matches = pd.concat([all_matches_df[all_matches_df['date'].dt.date < pd.Timestamp.now().date()], valid_matches])
    final_matches = pd.concat([all_matches_df[all_matches_df['date'].dt.date < pd.to_datetime("2023-05-27").dt.date], valid_matches])
    final_matches.sort_values(by=['team', 'date'], inplace=True)
    final_matches = final_matches.reset_index(drop=True)


    teams = final_matches['team'].unique().tolist()
    dfs = [final_matches[final_matches['team'] == x] for x in teams]
    dfs = [x.reset_index(drop=True) for x in dfs]

    valid_cols = final_matches.select_dtypes(include=['int8', 'int64', 'float64', 'int32']).columns.tolist()

    for df in dfs:
        for col in valid_cols:
            for i in range(df.shape[0]-1):
                val = df.loc[i, col]
                if pd.isnull(val):
                    if i == 0:
                        average = df[col].dropna().mean()
                        df.at[i, col] = average
                    else:
                        average = df[col][:i].dropna().mean()
                        df.at[i, col] = average

    return pd.concat(dfs).sort_values(by=['team', 'date']).reset_index(drop=True)

def get_overall_averages(final_matches, file=False):
    all_cols = final_matches.columns.tolist()
    if file:
        cols = all_cols[8:10] + all_cols[11:12] + all_cols[13:152] + all_cols[-1:]
    else:
        cols = all_cols[7:9] + all_cols[10:11] + all_cols[12:151] + all_cols[-1:]

    rolling_averages = final_matches.groupby('team')[cols].rolling(window=5, min_periods=3, closed='left').mean()
    rolling_averages.reset_index(level=0, drop=True, inplace=True)

    overall_averages = final_matches.groupby('team')[cols].apply(lambda x: x.shift().expanding().mean())
    overall_averages.reset_index(level=0, drop=True, inplace=True)

    return pd.concat([final_matches, rolling_averages.add_suffix('_rolling'), overall_averages.add_suffix('_mean')], axis=1)

def combine(df):
    home_table = df[df["venue"] == "Home"].sort_values(by=['date', 'time', 'team'])
    away_table = df[df["venue"] == "Away"].sort_values(by=['date', 'time', 'opponent'])
    home_table_renamed = home_table.rename(columns={"team": "home_team", "opponent": "away_team", "gf": "gf_home", "ga": "gf_away"})
    away_table_renamed = away_table.rename(columns={"team": "away_team", "opponent": "home_team", "gf": "gf_away", "ga": "gf_home"})

    merged_df = pd.merge(home_table_renamed, away_table_renamed, on=["date", "time", "home_team", "away_team", "gf_home", "gf_away"], suffixes=("_home", "_away"))
    merged_df["gf_home"] = merged_df["gf_home"].astype("int")
    merged_df["gf_away"] = merged_df["gf_away"].astype("int")
    return merged_df


def main():
    combine(get_overall_averages(clean_data(get_data("matches.csv")))).to_csv("data/cleaned_matches.csv")

