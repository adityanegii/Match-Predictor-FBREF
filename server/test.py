import pandas as pd
from sklearn.model_selection import ParameterGrid, train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
import data_processor as DP
import numpy as np
from xgboost import XGBRegressor
from xgboost import XGBClassifier
from sklearn import svm
from constants import *


from constants import DATE

def process(df, file=False):
    r_df = DP.combine(DP.get_overall_averages(DP.clean_data(df), file))
    r_df.to_csv(CLEAN_DATA)
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

def test_rf():
    matches_df = pd.read_csv(MATCH_FILE)
    matches_df["date"] = pd.to_datetime(matches_df["date"])
    matches_df = matches_df[matches_df["date"] < DATE]
    data = process(matches_df, True)

    predictors = get_predictors()

    data.dropna(inplace=True)
    X = data[predictors]
    y = data[["gf_home", "gf_away"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    param_grid_rf = {
    'n_estimators': [x for x in range(400, 3000, 200)],
    'max_depth': [None, 5, 10],
    'min_samples_split': [x for x in range (50, 500, 50)],
    'min_samples_leaf': [x for x in range(2, 20, 2)],
    'max_features': [1.0, 'sqrt', 'log2'],
    'random_state': [42]
    }   

    # RF results
    rf_best_result_score = -np.inf
    rf_best_scoreline_score = -np.inf
    rf_best_res_scores = []
    rf_best_scoreline_scores = []
    rf_best_result_params = None
    rf_best_scoreline_params = None

    for params in ParameterGrid(param_grid_rf):
        # Create an instance of the Random Forest classifier
        rf = RandomForestRegressor(**params)
        rf.fit(X_train, y_train)

        preds = rf.predict(X_test)
        combined = pd.DataFrame({
            # "Date": X_test["date"],
            # "Team": X_test["team"],
            # "Opponent": X_test["opponent"],
            "Predicted_GF_Home": preds[:, 0],  # Assuming "gf_home" is the first column in predictions
            "Predicted_GF_Away": preds[:, 1],  # Assuming "gf_away is the second column in predictions
            "Actual_GF_Home": y_test["gf_home"],
            "Actual_GF_Away": y_test["gf_away"]
        })

        combined["Predicted_GF_Home"] = combined["Predicted_GF_Home"].round(decimals = 0)
        combined["Predicted_GF_Away"] = combined["Predicted_GF_Away"].round(decimals = 0)

        total_games = combined.shape[0]
        correct_scores = combined[(combined["Predicted_GF_Home"] == combined["Actual_GF_Home"]) & (combined["Predicted_GF_Away"] == combined["Actual_GF_Away"])].shape[0]/total_games
        correct_home_wins = combined[(combined["Predicted_GF_Home"] > combined["Predicted_GF_Away"]) & (combined["Actual_GF_Home"] > combined["Actual_GF_Away"])].shape[0]/total_games
        correct_away_wins = combined[(combined["Predicted_GF_Home"] < combined["Predicted_GF_Away"]) & (combined["Actual_GF_Home"] < combined["Actual_GF_Away"])].shape[0]/total_games
        correct_draws = combined[(combined["Predicted_GF_Home"] == combined["Predicted_GF_Away"]) & (combined["Actual_GF_Home"] == combined["Actual_GF_Away"])].shape[0]/total_games
        total_scores = correct_home_wins + correct_away_wins + correct_draws

        if total_scores > rf_best_result_score:
            rf_best_result_score = total_scores
            rf_best_result_params = params
            rf_best_res_scores = [correct_home_wins, correct_away_wins, correct_draws, correct_scores]
        
        if correct_scores > rf_best_scoreline_score:
            rf_best_scoreline_score = correct_scores
            rf_best_scoreline_params = params
            rf_best_scoreline_scores = [correct_home_wins, correct_away_wins, correct_draws, correct_scores]

    print("---------------RF---------------")
    print("Best results params:", rf_best_result_params)
    print("Correct home wins:", rf_best_res_scores[0], "Correct away wins:", rf_best_res_scores[1], "Correct draws:", rf_best_res_scores[2], "Correct scores:", rf_best_res_scores[3])
    print("\n")
    print("Best score params:", rf_best_scoreline_params)
    print("Correct home wins:", rf_best_scoreline_scores[0], "Correct away wins:", rf_best_scoreline_scores[1], "Correct draws:", rf_best_scoreline_scores[2], "Correct scores:", rf_best_scoreline_scores[3])
    
def test_xgb():
    # Load and process the data
    matches_df = pd.read_csv(MATCH_FILE)
    matches_df["date"] = pd.to_datetime(matches_df["date"])
    matches_df = matches_df[matches_df["date"] < DATE]
    data = process(matches_df, True)
    predictors = get_predictors()
    data.dropna(inplace=True)
    X = data[predictors]
    y = data[["gf_home", "gf_away"]]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Parameter grids for XGBoost regressor and classifier
    param_grid_xgb_regressor = {
        'n_estimators': [x for x in range(400, 3000, 200)],
        'learning_rate': [0.1, 0.01, 0.001],
        'max_depth': [3, 5, 7, 9, None],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
        'reg_alpha': [0.0, 0.1, 0.5],
        'reg_lambda': [0.0, 0.1, 0.5],
        'random_state': [42],
    }

    param_grid_xgb_classifier = {
        'n_estimators': [x for x in range(400, 3000, 200)],
        'learning_rate': [0.1, 0.01, 0.001],
        'max_depth': [3, 5, 7, 9, None],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
        'reg_alpha': [0.0, 0.1, 0.5],
        'reg_lambda': [0.0, 0.1, 0.5],
        'objective': ['binary:logistic'],
        'random_state': [42],
    }

    # XGBoost regressor results
    xgb_regressor_best_score = -np.inf
    xgb_regressor_best_params = None

    for params in ParameterGrid(param_grid_xgb_regressor):
        # Create an instance of the XGBoost regressor
        xgb_regressor = XGBRegressor(**params)
        xgb_regressor.fit(X_train, y_train)

        preds = xgb_regressor.predict(X_test)
        combined = pd.DataFrame({
            "Predicted_GF_Home": preds[:, 0],  # Assuming "gf_home" is the first column in predictions
            "Predicted_GF_Away": preds[:, 1],  # Assuming "gf_away" is the second column in predictions
            "Actual_GF_Home": y_test["gf_home"],
            "Actual_GF_Away": y_test["gf_away"]
        })

        combined["Predicted_GF_Home"] = combined["Predicted_GF_Home"].round(decimals=0)
        combined["Predicted_GF_Away"] = combined["Predicted_GF_Away"].round(decimals=0)

        total_games = combined.shape[0]
        correct_scores = combined[(combined["Predicted_GF_Home"] == combined["Actual_GF_Home"]) &
                                (combined["Predicted_GF_Away"] == combined["Actual_GF_Away"])].shape[0] / total_games
        total_scores = correct_scores

        if total_scores > xgb_regressor_best_score:
            xgb_regressor_best_score = total_scores
            xgb_regressor_best_params = params

    print("---------------XGB Regressor---------------")
    print("Best results params:", xgb_regressor_best_params)
    print("Correct scores:", xgb_regressor_best_score)
    print()

    # XGBoost classifier results
    xgb_classifier_best_score = -np.inf
    xgb_classifier_best_params = None

    for params in ParameterGrid(param_grid_xgb_classifier):
        # Create an instance of the XGBoost classifier
        xgb_classifier = XGBClassifier(**params)
        xgb_classifier.fit(X_train, y_train)

        preds = xgb_classifier.predict(X_test)
        combined = pd.DataFrame({
            "Predicted_GF_Home": preds[:, 0],  # Assuming "gf_home" is the first column in predictions
            "Predicted_GF_Away": preds[:, 1],  # Assuming "gf_away" is the second column in predictions
            "Actual_GF_Home": y_test["gf_home"],
            "Actual_GF_Away": y_test["gf_away"]
        })

        combined["Predicted_GF_Home"] = combined["Predicted_GF_Home"].round(decimals=0)
        combined["Predicted_GF_Away"] = combined["Predicted_GF_Away"].round(decimals=0)

        total_games = combined.shape[0]
        correct_scores = combined[(combined["Predicted_GF_Home"] == combined["Actual_GF_Home"]) &
                                (combined["Predicted_GF_Away"] == combined["Actual_GF_Away"])].shape[0] / total_games
        total_scores = correct_scores

        if total_scores > xgb_classifier_best_score:
            xgb_classifier_best_score = total_scores
            xgb_classifier_best_params = params

    print("---------------XGB Classifier---------------")
    print("Best results params:", xgb_classifier_best_params)
    print("Correct scores:", xgb_classifier_best_score)

if __name__ == "__main__":
    test_rf()
    # test_mlp()
    test_xgb()
    # {'max_depth': None, 'max_features': 'log2', 'min_samples_leaf': 2, 'min_samples_split': 50, 'n_estimators': 1200, 'random_state': 42}
