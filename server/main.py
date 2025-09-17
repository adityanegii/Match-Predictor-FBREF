import scraper
import data_processor as DP

from constants import *

from models.classification.soft_voting import soft_voting
from models.regression.RandomForestRegressor import RFR
from models.classification.RandomForestClassifier import RFC
from models.regression.XGBRegressor import XGBR
from models.classification.XGBClassifier import XGBC
from models.classification.SVC import SVCWrapper
from models.classification.LR import LRWrapper

import pandas as pd

from database import SessionLocal
from data_models.Result import Result
from data_models.RawMatch import RawMatch
from sqlalchemy.dialects.sqlite import insert

import numpy as np

from utilities import get_predictors, map_predicted_result


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

def process(league: str) -> pd.DataFrame:
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
            # predict_c(model, type, train_set, next_games, predictors, league, session)

            # Train on full data and predict next games
            model.train_full(train_set, predictors)
            r_df = model.predict(next_games, predictors)
            r_df['Predicted_Winner'] = r_df.apply(map_predicted_result, axis=1)
            r_df = r_df.drop('Predicted_Result', axis=1)

            records = r_df.to_dict(orient='records')

            # Change column names to match Result model
            records = [{ 'date': record['Date'],
                         'home_team': record['Home_Team'],
                         'away_team': record['Away_Team'],
                         'league': league_full[league],
                         'model_type': type,
                         'home_win_prob': record.get('Prob_Home_Win', None),
                         'draw_prob': record.get('Prob_Draw', None),
                         'away_win_prob': record.get('Prob_Away_Win', None),
                        } for record in records]

            # Save to db
            try:
                stmt = insert(Result).values(records)

                stmt = stmt.on_conflict_do_update(
                    index_elements=['date', 'home_team', 'model_type'],
                    set_={
                        'away_team': stmt.excluded.away_team,
                        'league': stmt.excluded.league,
                        'home_win_prob': stmt.excluded.home_win_prob,
                        'draw_prob': stmt.excluded.draw_prob,
                        'away_win_prob': stmt.excluded.away_win_prob
                    }
                )

                session.execute(stmt)
                session.commit()
            except Exception as e:
                print(f"Error saving results to database for {league} with model {type}:\n{e}")
                session.rollback()
                raise e
            

            # r_df.to_csv("data/predictions_" + type + "_" + league + ".csv", index=False)
        soft_voting(["RFC", "XGBC", "SVC_1v1", "LR_1v1"], league, session)
        

        session.close()

        # for model, type in zip(models_r, types_r):
        #     predict_r(model, type, train_set, next_games, predictors, league)
        print("\n\n\n")

        

def main():
    scrape()
    train_and_predict()