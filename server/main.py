import scraper
import data_processor as DP

from constants import *

from models.RandomForestRegressor import RFR
from models.RandomForestClassifier import RFC
from models.XGBRegressor import XGBR
from models.XGBClassifier import XGBC

import pandas as pd

from database import SessionLocal
from data_models.RawMatch import RawMatch

def scrape():
    try:
    # Scrape Data
        session = SessionLocal()
        url = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"
        # url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        # url = "https://fbref.com/en/comps/11/Serie-A-Stats"
        # url = "https://fbref.com/en/comps/12/La-Liga-Stats"
        # url = "https://fbref.com/en/comps/13/Ligue-1-Stats"
        # url = "https://fbref.com/en/comps/20/Bundesliga-Stats"
        scraper.scrape(url, session)
    except Exception as e:
        print(e)
        print("Error with scraping")
    finally:
        session.close()

def process(league):
    try:
        league_name = league_full[league]

        session = SessionLocal()
        # query = f"SELECT * FROM matches WHERE league = '{league_name}'"
        matches_query = session.query(RawMatch).filter(RawMatch.comp == league_name).all()
        df = pd.DataFrame([match.as_dict() for match in matches_query])

        # Replace NaN values with 0 for all rows after DATE
        df.loc[df['date'].dt.date > pd.Timestamp(DATE).date(), :] = df.loc[df['date'].dt.date > pd.Timestamp(DATE).date(), :].fillna(0)

        r_df = DP.mark_promoted(DP.combine(DP.get_overall_averages(DP.clean_data(df))))
        r_df.to_csv("data/processed/process_" + league + ".csv", index=False)
    except Exception as e:
        print(e)
        print("Error with", league)
    finally:
        session.close()
    return r_df


def get_predictors():
    general = ["venue_code", "team_code", "day_code", "promoted"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg_per_sh"]
    # passing = ["totpasscmp", "totpassatt", "totpasscmp_pct", "totpassdist", "prgpassdist", "xag", "xa", "keypasses"]
    passing = ["xag", "xa", "keypasses"]
    gk = ["sota", "saves", "save_pct", "psxg"]
    ca = ["sca", "gca", "scalivepass", "gcalivepass"]
    # possesion = ["poss", "att3rdtouches", "attboxtouches", "atttakeons", "succtakeons", "carries", "totdistcarried", "prgdistcarried"]
    defense = ["tkl", "tklw", "tkldef3rd", "tklmid3rd", "tklatt3rd", "blocks", "int", "xga", "ga"]
    # misc = ["fouls", "foulsdrawn", "recov", "aerialwon_pct"]

    with open("data/cols.txt", "r") as f:
        cols = [line.strip() for line in f]
    
    base = [f"{x}_rolling" for x in cols] + [f"{x}_mean" for x in cols]
    predictors = [f"{x}_home" for x in base] + [f"{x}_away" for x in base]  + [f"{x}_home" for x in general] + [f"{x}_away" for x in general]
    
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
    try:
        r_df = model.train(train_set, predictors)
        res = model.evaluate_model(r_df)
        print("Accuracy", res)
        print("------------------PREDICTING " + type + "------------------")
        r_df = model.predict(next_games, predictors)
        r_df['Predicted_Winner'] = r_df.apply(map_predicted_result, axis=1)
        r_df = r_df.drop('Predicted_Result', axis=1)
        r_df.to_csv("data/predictions_" + type + "_" + league + ".csv", index=False)
    except Exception as e:
        print(e)
        print("Error with", league)

def predict_r(model, type, train_set, next_games, predictors, league):
    print("------------------TRAINING " + type + "------------------")
    try:
        r_df = model.train(train_set, predictors)
        c_s, c_r = model.evaluate_model(r_df)
        print("Correct Scores", c_s)
        print("Correct Results", c_r)
        print("------------------PREDICTING " + type + "------------------")
        r_df = model.predict(next_games, predictors)
        r_df.to_csv("data/predictions_" + type + "_" + league + ".csv", index=False)
    except Exception as e:
        print(e)
        print("Error with", league)

def train_and_predict():
    leauges = ["ENG1", "FRA1", "GER1", "ITA1", "SPA1"]
    predictors = get_predictors()
    for league in leauges:
        print("------------------" + league + "------------------")
        data = process(league)
        
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
        

def main():
    scrape()
    train_and_predict()