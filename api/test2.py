import pandas as pd
from sklearn.model_selection import ParameterGrid, train_test_split
import numpy as np

from constants import TEST_DATE
from RandomForestClassifier import RFC
from RandomForestRegressor import RFR
from XGBClassifier import XGBC
from XGBRegressor import XGBR

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

def setup():
    data = pd.read_csv("data/clean_data.csv")
    data["date"] = pd.to_datetime(data["date"])
    data = data[data["date"] < TEST_DATE]

    return data
    predictors = get_predictors()

    data.dropna(inplace=True)
    X = data[predictors]
    y = data[["gf_home", "gf_away"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    return X_train, X_test, y_train, y_test

def test_rf(data, predictors):
    param_grid_rf = {
    'n_estimators': [x for x in range(400, 3000, 200)],
    'max_depth': [None, 5, 10],
    'min_samples_split': [x for x in range (50, 500, 50)],
    'min_samples_leaf': [x for x in range(2, 20, 2)],
    'max_features': [1.0, 'sqrt', 'log2'],
    'random_state': [42]
    }   

    # RF results
    rfc_best_score = -np.inf
    rfc_best_params = None

    rfr_best_r_score = -np.inf
    rfr_best_r_params = None

    rfr_best_s_score = -np.inf
    rfr_best_s_params = None

    for params in ParameterGrid(param_grid_rf):
        rfc = RFC(params)
        res_df = rfc.train(data, predictors)
        score = rfc.evaluate_model(res_df)
        if score > rfc_best_score:
            rfc_best_score = score
            rfc_best_params = params
        
        rfr = RFR(params)
        res_df = rfr.train(data, predictors)
        c_scores, c_r = rfr.evaluate_model(res_df)
        if c_r > rfr_best_r_score:
            rfr_best_r_score = c_r
            rfr_best_r_params = params
        if c_scores > rfr_best_s_score:
            rfr_best_s_score = c_scores
            rfr_best_s_params = params
    
    return rfc_best_params, rfc_best_score, rfr_best_r_params, rfr_best_r_score, rfr_best_s_params, rfr_best_s_score

def test_xgb(data, predictors):
    xgb_param_grid = {
    'learning_rate': [0.01, 0.1, 0.2],
    'n_estimators': [x for x in range(400, 3000, 200)],
    'max_depth': [3, 5, 7, 9, None],
    'min_child_weight': [1, 3, 5],
    'gamma': [0, 0.1, 0.2],
    'subsample': [0.8, 0.9, 1.0],
    'colsample_bytree': [0.8, 0.9, 1.0],
    'reg_alpha': [0, 0.1, 0.5],
    'reg_lambda': [0, 0.1, 0.5],
    'random_state': [42],
    }

    # XGB results
    xgbc_best_score = -np.inf
    xgbc_best_params = None

    xgbr_best_r_score = -np.inf
    xgbr_best_r_params = None

    xgbr_best_s_score = -np.inf
    xgbr_best_s_params = None

    for params in ParameterGrid(xgb_param_grid):
        xgbc = XGBC(params)
        res_df = xgbc.train(data, predictors)
        score = xgbc.evaluate_model(res_df)
        if score > xgbc_best_score:
            xgbc_best_score = score
            xgbc_best_params = params
            
        xgbr = XGBR(params)
        res_df = xgbr.train(data, predictors)
        c_scores, c_r = xgbr.evaluate_model(res_df)
        if c_r > xgbr_best_r_score:
            xgbr_best_r_score = c_r
            xgbr_best_r_params = params
        if c_scores > xgbr_best_s_score:
            xgbr_best_s_score = c_scores
            xgbr_best_s_params = params
    
    return xgbc_best_params, xgbc_best_score, xgbr_best_r_params, xgbr_best_r_score, xgbr_best_s_params, xgbr_best_s_score

if __name__ == '__main__':
    data = setup()
    
    data = data.dropna()

    predictors = get_predictors()
    rfc_best_params, rfc_best_score, rfr_best_r_params, rfr_best_r_score, rfr_best_s_params, rfr_best_s_score = test_rf(data, predictors)
    print("RF Done")
    print(rfc_best_params, rfc_best_score, rfr_best_r_params, rfr_best_r_score, rfr_best_s_params, rfr_best_s_score)\
    
    xgbc_best_params, xgbc_best_score, xgbr_best_r_params, xgbr_best_r_score, xgbr_best_s_params, xgbr_best_s_score = test_xgb(data, predictors)
    print("XGB Done")
    print(xgbc_best_params, xgbc_best_score, xgbr_best_r_params, xgbr_best_r_score, xgbr_best_s_params, xgbr_best_s_score)

    df = pd.DataFrame(columns=["Model", "Score", "Params"])
    df.loc[0] = ["RandomForestClassifier", rfc_best_score, rfc_best_params]
    df.loc[1] = ["RandomForestRegressor (R)", rfr_best_r_score, rfr_best_r_params]
    df.loc[2] = ["RandomForestRegressor (S)", rfr_best_s_score, rfr_best_s_params]
    df.loc[3] = ["XGBClassifier", xgbc_best_score, xgbc_best_params]
    df.loc[4] = ["XGBRegressor (R)", xgbr_best_r_score, xgbr_best_r_params]
    df.loc[5] = ["XGBRegressor (S)", xgbr_best_s_score, xgbr_best_s_params]

    df.to_csv("data/model_results.csv", index=False)

