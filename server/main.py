import scraper
import data_processor as DP

from constants import *

from models.RandomForestRegressor import RFR
from models.RandomForestClassifier import RFC
from models.XGBRegressor import XGBR
from models.XGBClassifier import XGBC

import pandas as pd

def scrape():
    # Scrape Data
    years = list(range(2023, 2020, - 1))
    url = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"
    scraper.scrape(years, url)

def process(df, league):
    r_df = DP.combine(DP.get_overall_averages(DP.clean_data(df)))
    r_df.to_csv("data/process_" + league + ".csv", index=False)
    return r_df


def get_predictors():
    general = ["venue_code", "team_code", "day_code"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg/sh"]
    passing = ["totpasscmp", "totpassatt", "totpasscmp%", "totpassdist", "prgpassdist", "xag", "xa", "keypasses"]
    # gk = ["sota", "saves", "save%", "psxg"]
    ca = ["sca", "gca", "scalivepass", "gcalivepass"]
    possesion = ["poss", "att3rdtouches", "attboxtouches", "atttakeons", "succtakeons", "carries", "totdistcarried", "prgdistcarried"]
    defense = ["tkl", "tklw", "tkldef3rd", "tklmid3rd", "tklatt3rd", "blocks", "int"]
    misc = ["fouls", "foulsdrawn", "recov", "aerialwon%"]
    
    base = attacking + passing + ca + possesion + defense + misc
    base_averages = [f"{x}_rolling" for x in base] + [f"{x}_mean" for x in base]
    base_home_away = [f"{x}_home" for x in base_averages] + [f"{x}_away" for x in base_averages]
    predictors = [f"{x}_home" for x in general] + [f"{x}_away" for x in general] + base_home_away

    return predictors

def map_predicted_result(row):
    if row['Predicted_Result'] == 0:
        return row['Away_Team']
    elif row['Predicted_Result'] == 1:
        return 'Draw'
    elif row['Predicted_Result'] == 2:
        return row['Home_Team']

def predict_c(model, type, train_set, next_games, predictors, league):
    print("------------------TRAINING " + type + "------------------")
    r_df = model.train(train_set, predictors)
    res = model.evaluate_model(r_df)
    print("Accuracy", res)
    print("------------------PREDICTING " + type + "------------------")
    r_df = model.predict(next_games, predictors)
    r_df['Predicted_Winner'] = r_df.apply(map_predicted_result, axis=1)
    r_df = r_df.drop('Predicted_Result', axis=1)
    r_df.to_csv("data/predictions_" + type + "_" + league + ".csv", index=False)

def predict_r(model, type, train_set, next_games, predictors, league):
    print("------------------TRAINING " + type + "------------------")
    r_df = model.train(train_set, predictors)
    c_s, c_r = model.evaluate_model(r_df)
    print("Correct Scores", c_s)
    print("Correct Results", c_r)
    print("------------------PREDICTING " + type + "------------------")
    r_df = model.predict(next_games, predictors)
    r_df.to_csv("data/predictions_" + type + "_" + league + ".csv", index=False)

def train_and_predict():
    leauges = ["ENG1", "FRA1", "GER1", "ITA1", "SPA1"]
    predictors = get_predictors()
    for league in leauges:
        file = f"data/matches_{league}.csv"
        matches_df = pd.read_csv(file)
        # Convert date to date time
        matches_df["date"] = pd.to_datetime(matches_df["date"])
        # Drop future matches as their time is not certain and they are very far away
        matches_df = matches_df.dropna(subset=['time'])

        # Replace NaN values with 0 for all rows after DATE
        matches_df.loc[matches_df['date'].dt.date > pd.Timestamp(DATE).date(), :] = matches_df.loc[matches_df['date'].dt.date > pd.Timestamp(DATE).date(), :].fillna(0)

        data = process(matches_df, league)

        # train and predict
        train_set = data[data['date'].dt.date < pd.Timestamp(DATE).date()].dropna()
        num_nans = train_set.isna().sum().sum()
        if num_nans > 0:
            train_set = train_set.dropna()
        next_games = data[data['date'].dt.date >= pd.Timestamp(DATE).date()]

        rfc = RFC()
        rfr = RFR()
        xgbc = XGBC()
        xgbr = XGBR()

        models_c = [rfc, xgbc]
        models_r = [rfr, xgbr]
        types_c = ["RFC", "XGBC"]
        types_r = ["RFR", "XGBR"]

        print("------------------" + league + "------------------")
        for model, type in zip(models_c, types_c):
            predict_c(model, type, train_set, next_games, predictors, league)

        for model, type in zip(models_r, types_r):
            predict_r(model, type, train_set, next_games, predictors, league)

if __name__=='__main__':
    scrape()
    # train_and_predict()