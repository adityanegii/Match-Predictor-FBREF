# Match Predictor

This Match Predictor is a Python-based tool that uses various classifiers and regression models to predict match results and scorelines. The models are trained on data scraped from FBREF, which provides comprehensive football statistics.

## Features

- Predicts match results (win, draw, or loss) using classifiers:
  - Random Forest Classifier (RFC)
  - Extreme Gradient Boosting Classifier (XGBC)

- Predicts scorelines (goals for home and away teams) using regression models:
  - Random Forest Regressor (RFR)
  - Extreme Gradient Boosting Regressor (XGBR)

- Uses FBREF's scraped data for training and prediction.

## Requirements

Make sure you have a valid version of Python installed on your computer. This project was developped in 
Python 3.10. 

This project uses multiple libraries for the server (the Python backend). Make sure
to install them correctly using  `pip install -r requirements.txt`. (The last one (Requests) should
normally come with the default Python installation.

The following libraries are required to run the Match Predictor:

| Library | URL |
| ------- | ------------ |
| scikit-learn | https://scikit-learn.org/stable/install.html | 
| xgboost | https://xgboost.readthedocs.io/en/latest/build.html | 
| pandas | https://pandas.pydata.org/getting_started.html) | 
| numpy | https://numpy.org/ |
| bs4 | https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup | 
| Flask | https://flask.palletsprojects.com/en/3.0.x/ |
| flask_cors | https://flask-cors.readthedocs.io/en/latest/ |
| Requests | https://requests.readthedocs.io/en/latest/ |

Make sure to install the required libraries before running the Match Predictor.

## Running

First, make sure you run the app.py from the server directory. Then run `npm run dev` from the 
frontend directory. you might also have to run the main.py file from the server directory. 
This will take time (10-20mins) as it scrape for data and train the models and make the
predictions. This is still a feature I am working on to make faster and to have it done 
through the browser. Right now only the Premier League is implemented so choosing another league 
from the client will just cause a bad request.

To run a python file, first go into your terminal and go to the directory where the file you want to 
run is (so `cd <ENTER ABSOLUTE PATH TO SERVER DIRECTORY>`) and then use `python <filename>` for Windows and 
`python3 <filename>` for macOS and Linux.

## Acknowledgements

- The Match Predictor utilizes the scikit-learn and XGBoost libraries for machine learning models.
- It uses the pandas and numpy libraries to organize data and the bs4, and requests library to scrape the data.
- The data used in the predictor is sourced from FBREF (https://fbref.com/).
