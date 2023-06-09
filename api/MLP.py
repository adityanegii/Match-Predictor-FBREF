from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
import pandas as pd


class MLP():
    def __init__(self):
        self.model = MLPRegressor(hidden_layer_sizes=(64, 64), activation='relu', solver='adam', random_state=1, max_iter=1000)

    def train(self, data, predictors):
        X = data[predictors]
        y = data[['gf_home', 'gf_away']]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        
        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_test)

        # Create a new DataFrame with the desired columns
        result_df = X_test.copy()
        result_df['Date'] = data.loc[X_test.index, 'date']
        result_df['Home_Team'] = data.loc[X_test.index, 'home_team']
        result_df['Away_Team'] = data.loc[X_test.index, 'away_team']
        result_df['Actual_GF_Home'] = y_test['gf_home']
        result_df['Actual_GF_Away'] = y_test['gf_away']
        result_df['Predicted_GF_Home'] = preds[:, 0]  # Predicted goals for home team
        result_df['Predicted_GF_Away'] = preds[:, 1]  # Predicted goals for away team

        result_df['Predicted_GF_Home'] = result_df['Predicted_GF_Home'].round(decimals=0)
        result_df['Predicted_GF_Away'] = result_df['Predicted_GF_Away'].round(decimals=0)

        return result_df[['Date', 'Home_Team', 'Away_Team', 'Actual_GF_Home', 'Actual_GF_Away', 'Predicted_GF_Home', 'Predicted_GF_Away']]
    
    def predict(self, data, predictors):
        preds = self.model.predict(data[predictors])

        result_df = data.copy()
        result_df['date'] = data['date']
        result_df['home_team'] = data['home_team']
        result_df['away_team'] = data['away_team']
        result_df['predicted_gf_home'] = preds[:, 0]  # Predicted goals for home team
        result_df['predicted_gf_away'] = preds[:, 1]  # Predicted goals for away team

        result_df['predicted_gf_away']= result_df['predicted_gf_away'].round(decimals=0)
        result_df['predicted_gf_home']= result_df['predicted_gf_home'].round(decimals=0)

        return result_df[['date', 'home_team', 'away_team', 'predicted_gf_home', 'predicted_gf_away']]

    def evaluate_model(self, df):
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