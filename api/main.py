import scraper
import data_processor as DP

from constants import DATE

from RandomForestRegressor import RFR
from RandomForestClassifier import RFC
from XGBRegressor import XGBR
from XGBClassifier import XGBC
from SVMClassifier import SVC
from SVMRegressor import SVR

import pandas as pd

def scrape():
    # Scrape Data
    years = list(range(2023, 2020, - 1))
    url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    scraper.scrape(years, url)

def process(df, file=False):
    r_df = DP.combine(DP.get_overall_averages(DP.clean_data(df), file))
    r_df.to_csv("data/clean_data.csv")
    return r_df


def get_predictors():
    general = ["venue_code", "team_code", "day_code"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg/sh"]
    passing = ["totpasscmp", "totpassatt", "totpasscmp%", "totpassdist", "prgpassdist", "xag", "xa", "keypasses"]
    gk = ["sota", "saves", "save%", "psxg"]
    ca = ["sca", "gca", "scalivepass", "gcalivepass"]
    possesion = ["poss", "att3rdtouches", "attboxtouches", "atttakeons", "succtakeons", "carries", "totdistcarried", "prgdistcarried"]
    defense = ["tkl", "tklw", "tkldef3rd", "tklmid3rd", "tklatt3rd", "blocks", "int"]
    misc = ["fouls", "foulsdrawn", "recov", "aerialwon%"]
    
    base = attacking + passing + gk + ca + possesion + defense + misc
    base_averages = [f"{x}_rolling" for x in base] + [f"{x}_mean" for x in base]
    base_home_away = [f"{x}_home" for x in base_averages] + [f"{x}_away" for x in base_averages]
    predictors = [f"{x}_home" for x in general] + [f"{x}_away" for x in general] + base_home_away

    return predictors

def combine_predictions():
    pass

def predict_c(model, type, train_set, next_games, predictors, result_df=None):
    print("------------------TRAINING " + type + "------------------")
    r_df = model.train(train_set, predictors)
    res = model.evaluate_model(r_df)
    print("Accuracy", res)
    print("------------------PREDICTING " + type + "------------------")
    r_df = model.predict(next_games, predictors)
    r_df = r_df.rename(columns={'Predicted_Result': 'Predicted_Result_' + type})
    if result_df is None:
        return r_df
    return pd.merge(result_df, r_df, on=['Date', 'Home_Team', 'Away_Team'])

def predict_r(model, type, train_set, next_games, predictors, result_df=None):
    print("------------------TRAINING " + type + "------------------")
    r_df = model.train(train_set, predictors)
    c_s, c_r = model.evaluate_model(r_df)
    print("Correct Scores", c_s)
    print("Correct Results", c_r)
    print("------------------PREDICTING " + type + "------------------")
    r_df = model.predict(next_games, predictors)

    r_df["predicted_score_" + type] = r_df['predicted_gf_home'].astype(str) + '-' + r_df['predicted_gf_away'].astype(str)
    r_df = r_df.drop(['predicted_gf_home', 'predicted_gf_away'], axis=1)

    if result_df is None:
        return r_df
    return pd.merge(result_df, r_df, on=['date', 'home_team', 'away_team'])

def train_and_predict():
    matches_df = pd.read_csv("data/matches.csv")
    # Convert date to date time
    matches_df["date"] = pd.to_datetime(matches_df["date"])
    # Drop future matches as their time is not certain and they are very far away
    matches_df = matches_df.dropna(subset=['time'])

    # Replace NaN values with 0 for all rows after DATE
    matches_df.loc[matches_df['date'].dt.date > pd.Timestamp(DATE).date(), :] = matches_df.loc[matches_df['date'].dt.date > pd.Timestamp(DATE).date(), :].fillna(0)

    data = process(matches_df, True)

    predictors = get_predictors()

    # train and predict
    train_set = data[data['date'].dt.date < pd.Timestamp(DATE).date()].dropna()
    num_nans = train_set.isna().sum().sum()
    if num_nans > 0:
        train_set = train_set.dropna()
    next_games = data[data['date'].dt.date >= pd.Timestamp(DATE).date()]
    next_games.to_csv("data/next_games.csv", index=False)

    rfc = RFC()
    rfr = RFR()
    xgbc = XGBC()
    xgbr = XGBR()
    # svc = SVC()
    # svr = SVR()

    models_c = [rfc, xgbc]
    models_r = [rfr, xgbr]
    types_c = ["RFC", "XGBC"]
    types_r = ["RFR", "XGBR"]

    c_df = None
    r_df = None
    for model, type in zip(models_c, types_c):
        if c_df is None:
            c_df = predict_c(model, type, train_set, next_games, predictors)
        else:
            c_df = predict_c(model, type, train_set, next_games, predictors, c_df)
    c_df.to_csv("data/predictions_c.csv", index=False)

    for model, type in zip(models_r, types_r):
        if r_df is None:
            r_df = predict_r(model, type, train_set, next_games, predictors)
        else:
            r_df = predict_r(model, type, train_set, next_games, predictors, r_df)
    r_df.to_csv("data/predictions_r.csv", index=False)

if __name__=='__main__':
    # scrape()
    train_and_predict()