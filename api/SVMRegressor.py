from sklearn.model_selection import train_test_split
from sklearn import svm

class SVR:
    def __init__(self):
        self.model_home = svm.SVR()
        self.model_away = svm.SVR()
        
    def train(self, data, predictors):
        X = data[predictors]
        y_home = data['gf_home']
        y_away = data['gf_away']

        X_train, X_test, y_train_home, y_test_home, y_train_away, y_test_away = train_test_split(X, y_home, y_away, test_size=0.25, random_state=42)
        
        self.model_home.fit(X_train, y_train_home)
        self.model_away.fit(X_train, y_train_away)
        
        preds_home = self.model_home.predict(X_test)
        preds_away = self.model_away.predict(X_test)

        # Create a new DataFrame with the desired columns
        result_df = X_test.copy()
        result_df['Date'] = data.loc[X_test.index, 'date']
        result_df['Home_Team'] = data.loc[X_test.index, 'home_team']
        result_df['Away_Team'] = data.loc[X_test.index, 'away_team']
        result_df['Actual_GF_Home'] = y_test_home
        result_df['Actual_GF_Away'] = y_test_away
        result_df['Predicted_GF_Home'] = preds_home.round(decimals=0)
        result_df['Predicted_GF_Away'] = preds_away.round(decimals=0)

        return result_df[['Date', 'Home_Team', 'Away_Team', 'Actual_GF_Home', 'Actual_GF_Away', 'Predicted_GF_Home', 'Predicted_GF_Away']]

    def predict(self, data, predictors):
        X = data[predictors]

        preds_home = self.model_home.predict(X)
        preds_away = self.model_away.predict(X)

        # Create a new DataFrame with the desired columns
        result_df = data.copy()
        result_df['predicted_gf_home'] = preds_home.round(decimals=0)
        result_df['predicted_gf_away'] = preds_away.round(decimals=0)

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