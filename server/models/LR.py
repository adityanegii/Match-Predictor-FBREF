from sklearn.preprocessing import StandardScaler
from sklearn.multiclass import OneVsOneClassifier
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pandas as pd

class LRWrapper:
    def __init__(self, params=None):
        self.scaler = StandardScaler()

        if params:
            self.model = OneVsOneClassifier(LogisticRegression(**params))
        else:
            self.model = OneVsOneClassifier(LogisticRegression(solver='lbfgs', max_iter=1000))

    def train(self, data, predictors):
        X = data[predictors]
        y = data['result_code']

        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(X_scaled, y, data.index, test_size=0.25, random_state=42)

        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)

        # Create a new DataFrame with the desired columns
        result_df = pd.DataFrame({
        'Date': data.loc[idx_test, 'date'],
        'Home_Team': data.loc[idx_test, 'home_team'],
        'Away_Team': data.loc[idx_test, 'away_team'],
        'Actual_Result': y_test,
        'Predicted_Result': preds
        }, index=idx_test)

        return result_df

    def predict(self, data, predictors):
        X = data[predictors]

        X_scaled = self.scaler.transform(X)
        preds = self.model.predict(X_scaled)
        preds = self.model.decision_function(X_scaled)
        preds = np.exp(preds) / np.sum(np.exp(preds), axis=1, keepdims=True)  # Softmax to get probabilities

        # Create a new DataFrame with the desired columns
        result_df = data.copy()
        result_df['Date'] = data['date']
        result_df['Home_Team'] = data['home_team']
        result_df['Away_Team'] = data['away_team']
        result_df['Predicted_Result'] = np.argmax(preds, axis=1)  # Predicted result of the game
        
        # Add predicted probabilities for each class to the DataFrame
        result_df['Prob_Home_Win'] = (preds[:, 2] * 100).round(1)
        result_df['Prob_Draw'] = (preds[:, 1] * 100).round(1)
        result_df['Prob_Away_Win'] = (preds[:, 0] * 100).round(1)

        return result_df[['Date', 'Home_Team', 'Away_Team', 'Predicted_Result', 'Prob_Home_Win', 'Prob_Draw', 'Prob_Away_Win']]

    def evaluate_model(self, df):
        correct_results = df[df["Predicted_Result"] == df["Actual_Result"]].shape[0]
        total_games = df.shape[0]
        return correct_results/total_games