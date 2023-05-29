import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


def get_data(file):
    return pd.read_csv(file)

def train(data, predictors, rf):
    X = data[predictors]
    y = data[['gf_home', 'gf_away']]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    rf.fit(X_train, y_train)
    preds = rf.predict(X_test)

    # Create a new DataFrame with the desired columns
    result_df = X_test.copy()
    result_df['Date'] = data.loc[X_test.index, 'date']
    result_df['Home_Team'] = data.loc[X_test.index, 'home_team']
    result_df['Away_Team'] = data.loc[X_test.index, 'away_team']
    result_df['Actual_GF_Home'] = y_test['gf_home']
    result_df['Actual_GF_Away'] = y_test['gf_away']
    result_df['Predicted_GF_Home'] = preds[:, 0]  # Predicted goals for home team
    result_df['Predicted_GF_Away'] = preds[:, 1]  # Predicted goals for away team
    return result_df[['Date', 'Home_Team', 'Away_Team', 'Actual_GF_Home', 'Actual_GF_Away', 'Predicted_GF_Home', 'Predicted_GF_Away']]

def predict(data, predictors, rf):
    X = data[predictors]
    y = data[['gf_home', 'gf_away']]

    preds = rf.predict(X)

    # Create a new DataFrame with the desired columns
    result_df = data.copy()
    result_df['date'] = data['date']
    result_df['home_team'] = data['home_team']
    result_df['away_team'] = data['away_team']
    result_df['predicted_gf_home'] = preds[:, 0]  # Predicted goals for home team
    result_df['predicted_gf_away'] = preds[:, 1]  # Predicted goals for away team

    return result_df[['date', 'home_team', 'away_team', 'predicted_gf_home', 'predicted_gf_away']]

def initialize():
    general = ["venue_code", "team_code", "day_code"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg/sh", "attboxtouches"]
    passing = ["totpasscmp", "totpassatt", "totpasscmp%", "totpassdist", "prgpassdist", "xag", "xa", "keypasses"]
    gk = ["sota", "saves", "save%", "psxg", "passlaunch%", "gklaunch%"]
    ca = ["sca", "gca", "scalivepass", "gcalivepass"]
    possesion = ["poss", "att3rdtouches", "attboxtouches", "atttakeons", "succtakeons", "carries", "totdistcarried", "prgdistcarried"]
    defense = ["tkl", "tklw", "tkldef3rd", "tklmid3rd", "tklatt3rd", "blocks", "int"]
    misc = ["fouls", "foulsdrawn", "recov", "aerialwon%"]
    
    base = attacking + passing + gk + ca + possesion + defense + misc
    base_averages = [f"{x}_rolling" for x in base] + [f"{x}_mean" for x in base]
    base_home_away = [f"{x}_home" for x in base_averages] + [f"{x}_away" for x in base_averages]
    predictors = [f"{x}_home" for x in general] + [f"{x}_away" for x in general] + base_home_away

    rf = RandomForestClassifier(n_estimators=400, min_samples_split=50, min_samples_leaf=4, random_state=42)

    return (predictors, rf)

def evaluate_model(df):
    correct_scores = df[(df["Predicted_GF_Home"] == df["Actual_GF_Home"]) & (df["Predicted_GF_Away"] == df["Actual_GF_Away"])].shape[0]
    correct_home_wins = df[(df["Predicted_GF_Home"] > df["Predicted_GF_Away"]) & (df["Actual_GF_Home"] > df["Actual_GF_Away"])].shape[0]
    correct_away_wins = df[(df["Predicted_GF_Home"] < df["Predicted_GF_Away"]) & (df["Actual_GF_Home"] < df["Actual_GF_Away"])].shape[0]
    correct_draws = df[(df["Predicted_GF_Home"] == df["Predicted_GF_Away"]) & (df["Actual_GF_Home"] == df["Actual_GF_Away"])].shape[0]
    total_games = df.shape[0]
    print("correct scores:", correct_scores/total_games)
    print("correct home wins:", correct_home_wins/total_games)
    print("correct away wins:", correct_away_wins/total_games)
    print("correct draws:", correct_draws/total_games)
    print("correct results:", (correct_home_wins + correct_away_wins + correct_draws)/total_games)

def main():
    predictors, rf = initialize()
    data = get_data("cleaned_matches.csv")
    print("------------------TRAINING------------------")
    evaluate_model(train(data.dropna(), predictors, rf))
    print("------------------PREDICTING------------------")
    next_games = data[data['date'] >= pd.Timestamp.now().date()]
    predict(data, predictors, rf).to_csv("data/predictions.csv", index=False)



