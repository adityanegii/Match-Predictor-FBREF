from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

class XGBC():
    def __init__(self, params=None):
        if params:
            self.model = XGBClassifier(**params)
        else:
            self.model = XGBClassifier(n_estimators=4000, subsample=0.95, random_state=42)
        
    def train(self, data, predictors, split=0.25):
        X = data[predictors]
        y = data['result_code']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split, random_state=42)

        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_test)

        # Create a new DataFrame with the desired columns
        result_df = X_test.copy()
        result_df['Date'] = data.loc[X_test.index, 'date']
        result_df['Home_Team'] = data.loc[X_test.index, 'home_team']
        result_df['Away_Team'] = data.loc[X_test.index, 'away_team']
        result_df['Actual_Result'] = y_test  # Actual result of the game
        result_df['Predicted_Result'] = preds  # Predicted result of the game

        return result_df[['Date', 'Home_Team', 'Away_Team', 'Actual_Result', 'Predicted_Result']]
    
    def train_full(self, data, predictors):
        X = data[predictors]
        y = data['result_code']
        
        self.model.fit(X, y)

    def predict(self, data, predictors):
        X = data[predictors]
        y = data['result_code']

        preds = self.model.predict(X)
        probs = self.model.predict_proba(X)  # Obtain the predicted probabilities

        # Create a new DataFrame with the desired columns
        result_df = data.copy()
        result_df['Date'] = data['date']
        result_df['Home_Team'] = data['home_team']
        result_df['Away_Team'] = data['away_team']
        result_df['Predicted_Result'] = preds  # Predicted result of the game

        # Add predicted probabilities for each class to the DataFrame
        result_df['Prob_Home_Win'] = (probs[:, 2] * 100).round(1)
        result_df['Prob_Draw'] = (probs[:, 1] * 100).round(1)
        result_df['Prob_Away_Win'] = (probs[:, 0] * 100).round(1)

        return result_df[['Date', 'Home_Team', 'Away_Team', 'Predicted_Result', 'Prob_Home_Win', 'Prob_Draw', 'Prob_Away_Win']]

    def evaluate_model(self, df):
        correct_results = df[df["Predicted_Result"] == df["Actual_Result"]].shape[0]
        total_games = df.shape[0]

        return correct_results/total_games




