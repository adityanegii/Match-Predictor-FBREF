# Match Predictor

This Match Predictor is a Python-based tool that uses various classifiers and regression models to predict match results and scorelines. The models are trained on data scraped from FBREF, which provides comprehensive football statistics.

## Features

- Predicts match results (win, draw, or loss) using classifiers:
  - Random Forest Classifier (RFC)
  - Support Vector Classifier (SVC)
  - Extreme Gradient Boosting Classifier (XGBC)

- Predicts scorelines (goals for home and away teams) using regression models:
  - Random Forest Regressor (RFR)
  - Support Vector Regressor (SVR)
  - Extreme Gradient Boosting Regressor (XGBR)

- Uses FBREF's scraped data for training and prediction.

## Acknowledgements

- The Match Predictor utilizes the scikit-learn and XGBoost libraries for machine learning models.
- The data used in the predictor is sourced from FBREF (https://fbref.com/).
