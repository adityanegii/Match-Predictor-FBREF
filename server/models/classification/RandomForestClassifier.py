from sklearn.ensemble import RandomForestClassifier

from models.classification.TreeBasedClassifier import TreeBasedClassifier

class RFC(TreeBasedClassifier):
    def __init__(self, params: dict = None):
        if params:
            super().__init__(RandomForestClassifier(**params))
        else:
            super().__init__(RandomForestClassifier(n_estimators=2400, min_samples_split=150, min_samples_leaf=10, class_weight='balanced', random_state=42))
        
    # def train(self, data: pd.DataFrame, predictors: list) -> None:
    #     X = data[predictors]
    #     y = data['result_code']
        
    #     self.model.fit(X, y)

    # def predict(self, data: pd.DataFrame, predictors: list) -> pd.DataFrame:
    #     X = data[predictors]
    #     y = data['result_code']
        
    #     probs = self.model.predict_proba(X)  # Obtain the predicted probabilities
    #     preds = np.argmax(probs, axis=1)  # Get the class with the highest probability

    #     # Create a new DataFrame with the desired columns
    #     result_df = data.copy()
    #     result_df['Date'] = data['date']
    #     result_df['Home_Team'] = data['home_team']
    #     result_df['Away_Team'] = data['away_team']
    #     result_df['Predicted_Result'] = preds  # Predicted result of the game

    #     # Add predicted probabilities for each class to the DataFrame
    #     result_df['Prob_Home_Win'] = (probs[:, 2] * 100).round(1)
    #     result_df['Prob_Draw'] = (probs[:, 1] * 100).round(1)
    #     result_df['Prob_Away_Win'] = (probs[:, 0] * 100).round(1)

    #     return result_df[['Date', 'Home_Team', 'Away_Team', 'Predicted_Result', 'Prob_Home_Win', 'Prob_Draw', 'Prob_Away_Win']]

    # def evaluate_model(self, data:pd.DataFrame, predictors: list) -> pd.DataFrame:
    #     X = data[predictors]
    #     y = data['result_code']

    #     probs = self.model.predict_proba(X)  # Obtain the predicted probabilities
    #     preds = np.argmax(probs, axis=1)  # Get the class with the highest probability

    #     # Create a df with actual vs predicted and probabilities
    #     result_df = pd.DataFrame({
    #         'Actual_Result': y,
    #         'Predicted_Result': preds,
    #         'Prob_Home_Win': (probs[:, 2] * 100).round(1),
    #         'Prob_Draw': (probs[:, 1] * 100).round(1),
    #         'Prob_Away_Win': (probs[:, 0] * 100).round(1)
    #     }, index=data.index)

    #     return result_df




