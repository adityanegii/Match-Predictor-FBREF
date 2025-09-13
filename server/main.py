import scraper
import data_processor as DP

from constants import *

from models.RandomForestRegressor import RFR
from models.RandomForestClassifier import RFC
from models.XGBRegressor import XGBR
from models.XGBClassifier import XGBC
from models.SVC import SVCWrapper
from models.LR import LRWrapper

import pandas as pd

from database import SessionLocal
from data_models.Result import Result
from data_models.RawMatch import RawMatch
from sqlalchemy import insert, update, bindparam

import numpy as np


def scrape():
    try:
    # Scrape Data
        session = SessionLocal()
        # url = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"
        url = "https://fbref.com/en/comps/9/Premier-League-Stats"
        # url = "https://fbref.com/en/comps/11/Serie-A-Stats"
        # url = "https://fbref.com/en/comps/12/La-Liga-Stats"
        # url = "https://fbref.com/en/comps/13/Ligue-1-Stats"
        # url = "https://fbref.com/en/comps/20/Bundesliga-Stats"
        scraper.scrape(url, session)
    except Exception as e:
        print(f"Error with scraping:\n{e}")
        raise e 
    finally:
        session.close()

def process(league):
    try:
        league_name = league_full[league]

        session = SessionLocal()
        # query = f"SELECT * FROM matches WHERE league = '{league_name}'"
        matches_query = session.query(RawMatch).filter(RawMatch.comp == league_name).all()

        if not matches_query:
            print(f"No matches found for league: {league_name}")
            return pd.DataFrame()

        df = pd.DataFrame([match.as_dict() for match in matches_query])

        # Replace NaN values with 0 for all rows after DATE
        df.loc[df['date'].dt.date > pd.Timestamp(DATE).date(), :] = df.loc[df['date'].dt.date > pd.Timestamp(DATE).date(), :].fillna(0)

        r_df = DP.mark_promoted(DP.combine(DP.calculate_team_results_and_points(DP.get_averages(DP.clean_data(df)))))
        r_df.to_csv("data/processed/process_" + league + ".csv", index=False)
    except Exception as e:
        print(f"Error processing {league}:\n{e}")
        raise e
    finally:
        session.close()
    return r_df

def get_predictors_basic():
    general = ["venue_code", "team_code", "day_code", "promoted"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg_per_sh"]
    defense = ["int", "xga", "ga"]
    gk = ["sota", "saves", "save_pct", "psxg"]

    base = attacking + defense + gk
    home_stats = [f"{x}_home_rolling" for x in base] + [f"{x}_home_mean" for x in base]
    away_stats = [f"{x}_away_rolling" for x in base] + [f"{x}_away_mean" for x in base]
    home_stats = [f"{x}_home" for x in home_stats] + [f"{x}_away" for x in home_stats]
    away_stats = [f"{x}_home" for x in away_stats] + [f"{x}_away" for x in away_stats]
    overall_home = [f"{x}_rolling_home" for x in base] + [f"{x}_mean_home" for x in base]
    overall_away = [f"{x}_rolling_away" for x in base] + [f"{x}_mean_away" for x in base]
    predictors = [f"{x}_home" for x in general] + [f"{x}_away" for x in general] + home_stats + away_stats + overall_home + overall_away
    return predictors



def get_predictors():
    general = ["venue_code", "team_code", "day_code", "promoted"]
    attacking = ["gf", "xg", "sh", "sot", "npxg", "npxg_per_sh"]
    # passing = ["totpasscmp", "totpassatt", "totpasscmp_pct", "totpassdist", "prgpassdist", "xag", "xa", "keypasses"]
    passing = ["xag", "xa", "keypasses"]
    gk = ["sota", "saves", "save_pct", "psxg"]
    ca = ["sca", "gca", "sca_live_pass", "gca_live_pass"]
    # possesion = ["poss", "att3rdtouches", "attboxtouches", "atttakeons", "succtakeons", "carries", "totdistcarried", "prgdistcarried"]
    defense = ["tkls", "tkls_won", "tkls_def_3rd", "tkls_mid_3rd", "tkls_att_3rd", "blocks", "int", "xga", "ga"]
    # misc = ["fouls", "foulsdrawn", "recov", "aerialwon_pct"]

    base = attacking + passing + gk + ca + defense
    overall_home = [f"{x}_rolling_home" for x in base] + [f"{x}_mean_home" for x in base]
    overall_away = [f"{x}_rolling_away" for x in base] + [f"{x}_mean_away" for x in base]

    home_stats = [f"{x}_home_rolling" for x in base] + [f"{x}_home_mean" for x in base]
    away_stats = [f"{x}_away_rolling" for x in base] + [f"{x}_away_mean" for x in base]

    home_stats = [f"{x}_home" for x in home_stats] + [f"{x}_away" for x in home_stats]
    away_stats = [f"{x}_home" for x in away_stats] + [f"{x}_away" for x in away_stats]

    predictors = [f"{x}_home" for x in general] + [f"{x}_away" for x in general] + home_stats + away_stats + overall_home + overall_away

    # with open("data/cols.txt", "r") as f:
    #     cols = [line.strip() for line in f]
    
    # base = [f"{x}_rolling" for x in cols] + [f"{x}_mean" for x in cols]
    # predictors = [f"{x}_home" for x in base] + [f"{x}_away" for x in base]  + [f"{x}_home" for x in general] + [f"{x}_away" for x in general]
    
    # return predictors
    return get_predictors_basic()

def map_predicted_result(row):
    if row['Predicted_Result'] == 0:
        return row['Away_Team']
    elif row['Predicted_Result'] == 1:
        return 'Draw'
    elif row['Predicted_Result'] == 2:
        return row['Home_Team']

def predict_c(model, type, train_set, next_games, predictors, league, session):
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
        print("Error with", league)
        print(e)
        raise e

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
        print("Error with", league)
        print(e)
        raise e

def soft_voting(models: list[str], league: str):
    # Open csvs
    dfs = [pd.read_csv(f"data/predictions_{model}_{league}.csv") for model in models]

    # Stack probabilities and compute average
    prob_home = np.mean([df['Prob_Home_Win'].values / 100 for df in dfs], axis=0)
    prob_draw = np.mean([df['Prob_Draw'].values / 100 for df in dfs], axis=0)
    prob_away = np.mean([df['Prob_Away_Win'].values / 100 for df in dfs], axis=0)

    # Determine final predicted result (0=Away,1=Draw,2=Home)
    avg_probs = np.vstack([prob_away, prob_draw, prob_home]).T
    final_preds = np.argmax(avg_probs, axis=1)

    # Build result DataFrame
    result_df = dfs[0][['Date', 'Home_Team', 'Away_Team']].copy()
    result_df['Predicted_Result'] = final_preds
    result_df['Prob_Home_Win'] = (prob_home * 100).round(1)
    result_df['Prob_Draw'] = (prob_draw * 100).round(1)
    result_df['Prob_Away_Win'] = (prob_away * 100).round(1)

    result_df.to_csv(f"data/predictions_Ensemble_{league}.csv", index=False)


def train_and_predict():
    session = SessionLocal()

    leagues = ["ENG1", "FRA1", "GER1", "ITA1", "SPA1"]
    predictors = get_predictors()
    for league in leagues:
        print("------------------" + league + "------------------")
        data = process(league)
        
        if data.empty:
            continue
        # train and predict
        train_set = data[data['date'].dt.date < pd.Timestamp(DATE).date()]
        
        num_nans = train_set.isna().sum().sum()

        if num_nans > 0:
            train_set = train_set.dropna()

        next_games = data[data['date'].dt.date >= pd.Timestamp(DATE).date()]

        rfc = RFC()
        # rfr = RFR()
        xgbc = XGBC()
        # xgbr = XGBR()
        svc = SVCWrapper()
        lr = LRWrapper()

        models_c = [rfc, xgbc, svc, lr]
        # models_r = [rfr, xgbr]
        types_c = ["RFC", "XGBC", "SVC_1v1", "LR_1v1"]
        # types_r = ["RFR", "XGBR"]

        for model, type in zip(models_c, types_c):
            predict_c(model, type, train_set, next_games, predictors, league, session)
        
        session.close()

        soft_voting(["RFC", "XGBC", "SVC_1v1", "LR_1v1"], league)
        # for model, type in zip(models_r, types_r):
        #     predict_r(model, type, train_set, next_games, predictors, league)
        print("\n\n\n")

        

def main():
    scrape()
    train_and_predict()