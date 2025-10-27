from sklearn.preprocessing import StandardScaler
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
import numpy as np
import pandas as pd

from models.classification.ClassifierBase import ClassifierBase

class LinearClassifierBase(ClassifierBase):
    def __init__(self, model, one_vs_rest: bool = False):
        self.scaler = StandardScaler()

        if one_vs_rest:
            self.model = OneVsRestClassifier(model)
        else:
            self.model = OneVsOneClassifier(model)
        
    def train(self, data, predictors):
        X = data[predictors]
        y = data['result_code']

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, data, predictors):
        X = data[predictors]

        X_scaled = self.scaler.transform(X)
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

    def evaluate_model(self, data:pd.DataFrame, predictors: list) -> pd.DataFrame:
        X = data[predictors]
        y = data['result_code']

        X_scaled = self.scaler.transform(X)
        probs = self.model.decision_function(X_scaled)
        probs = np.exp(probs) / np.sum(np.exp(probs), axis=1, keepdims=True)  # Softmax to get probabilities
        preds = np.argmax(probs, axis=1)  # Get the class with the highest probability

        # Create a df with actual vs predicted and probabilities
        result_df = pd.DataFrame({
            'Actual_Result': y,
            'Predicted_Result': preds,
            'Prob_Home_Win': (probs[:, 2] * 100).round(1),
            'Prob_Draw': (probs[:, 1] * 100).round(1),
            'Prob_Away_Win': (probs[:, 0] * 100).round(1)
        }, index=data.index)

        return result_df