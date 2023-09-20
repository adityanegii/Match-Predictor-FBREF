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

## Requirements

The following libraries are required to run the Match Predictor:

| Library | Download URL | Installation |
| ------- | ------------ | ------------ |
| Python | https://www.python.org/downloads/ | Follow instructions in link |
| scikit-learn | https://scikit-learn.org/stable/install.html | `pip install scikit-learn` |
| xgboost | https://xgboost.readthedocs.io/en/latest/build.html | `pip install xgboost` |
| pandas | https://pandas.pydata.org/getting_started.html) | `pip install pandas` |
| bs4 | https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup | `pip install beautifulsoup4` |

Make sure to install the required libraries before running the Match Predictor.

## Acknowledgements

- The Match Predictor utilizes the scikit-learn and XGBoost libraries for machine learning models.
- It uses the pandas library to organize data and the bs4, and requests library to scrape the data.
- The data used in the predictor is sourced from FBREF (https://fbref.com/).
