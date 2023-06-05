import scraper
import data_processor as DP

from RandomForestRegressor import RFR
from RandomForestClassifier import RFC
from XGBRegressor import XGBR
from XGBClassifier import XGBC
from SVMClassifier import SVC
from SVMRegressor import SVR

import pandas as pd

def scrape(years, url): 
    return scraper.scrape(years, url)

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

def predict(model, type, train_set, next_games, predictors):
    print("------------------TRAINING " + type + "------------------")
    r_df = model.train(train_set, predictors)
    model.evaluate_model(r_df)
    print("------------------PREDICTING " + type + "------------------")
    r_df = model.predict(next_games, predictors)
    r_df.to_csv("data/predictions_" + type + ".csv", index=False)

def main():
    # Scrape Data
    # years = list(range(2022, 2020, - 1))
    # url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    # matches_df = scrape(years, url)
    # data = process(matches_df)

    matches_df = pd.read_csv("data/matches.csv")
    data = process(matches_df, True)

    predictors = get_predictors()

    train_set = data[data['date'].dt.date < pd.Timestamp('2023-05-27').date()].dropna()
    next_games = data[data['date'].dt.date >= pd.Timestamp('2023-05-27').date()]

    rfc = RFC()
    rfr = RFR()
    xgbc = XGBC()
    xgbr = XGBR()
    svc = SVC()
    svr = SVR()

    models = [rfc, rfr, xgbc, xgbr, svc, svr]
    types = ["RFC", "RFR", "XGBC", "XGBR", "SVC", "SVR"]

    for model, type in zip(models, types):
        predict(model, type, train_set, next_games, predictors)

main()