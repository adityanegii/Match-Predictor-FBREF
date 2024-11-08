# Match Predictor

This Match Predictor is a Python-based tool that uses various classifiers and regression models to predict match results and scorelines. The models are trained on data scraped from FBREF, which provides comprehensive football statistics.

## Features

- Predicts match result probability (win, draw, or loss) using classifiers:
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
frontend directory. I have included the predictions for a recent Matchweek (check the predicitions*.csv to see exactly which matchweek it is) if you are interested in seeing the functionality of this project quickly. 

If you want to see the predictions for the set of upcoming fixtures, press the train and predict button on your browser.
This will take time as it scrapes for data, trains the models, and make the predictions. This is still a feature 
I am working on to make faster

To run a python file, first go into your terminal and go to the directory where the file you want to 
run is (so `cd <ENTER ABSOLUTE PATH TO SERVER DIRECTORY>`) and then use `python <filename>` for Windows and 
`python3 <filename>` for macOS and Linux.

When on the browser, you can press the scrape button to scrape the data from FBREF. This will take a while. Conversly you can press the train and predict button to train the models and make predictions from existing data (this option will not be available since there is no data to start with). You can also check the predictions for different models by selecting from the drop down menus (this is available since I have included recent prediction files).

## Acknowledgements

- The Match Predictor utilizes the scikit-learn and XGBoost libraries for machine learning models.
- It uses the pandas and numpy libraries to organize data and the bs4, and requests library to scrape the data.
- The data used in the predictor is sourced from FBREF (https://fbref.com/).
