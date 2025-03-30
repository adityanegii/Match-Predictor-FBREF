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

- Uses SQLite and SQLAlchemy to store raw data that has been scraped in order to shorten scraping times.

## Running

Open up a terminal and navigate to the directory where the project is located.

First create a virtual environment using `python -m venv venv` on Windows or `python3 -m venv venv` on macOS or Linux and then activate it using `venv/scripts/activate` on Windows`source venv/bin/activate` for macOS and Linux. Then install the required libraries using `pip install -r requirements.txt`.

Then navigate to the server directory and run the app.py file using `python app.py` on Windows or `python3 app.py` on macOS and Linux. This will start the server. Then in another terminal window navigate to the web client directory and run `npm install` to install the required libraries. Then run `npm run dev` to start the frontend. This will open up a browser window with the Match Predictor on `http://localhost:3000/`.

I have included the predictions for one Matchweek (check the predicitions*.csv to see exactly which matchweek it is) if you are interested in seeing the functionality of this project quickly and just seeing the display function. 

If you want to see the predictions for the set of upcoming fixtures, press the "Scrape" button to retrieve the new data, then after the data has been scraped click the "Train Models" button to train and make predictions. This is still a feature I am working on to make faster and more efficient. If you just want to scrape for 1 league in particular, you can change the url to scrape in the `main.py` file in the scrape function. I have commented out the urls for the the top 5 leagues individually, and left the url for the whole top 5 leagues combined. Currently the initial scrape will take around 4-5 hours (for all the leagues), however the subsequent scrapes will only take 1/4-1/5 of the intial time. Instead of rescraping all the match data, with SQLite and SQLAlchemy, I store all the previous years if they are already present in the database, and only scrape the current year. So for only 1 league it should be ~1 hour for the initial scrape then 15-20 mins for the subsequent scrapes.

## Requirements

Make sure you have a valid version of Python installed on your computer. This project was developped in 
Python 3.10. 

This project uses multiple libraries for the server (the Python backend). Make sure
to install them correctly using  `pip install -r requirements.txt`. 

The following libraries are required to run the Match Predictor (I have only listed the main ones, install the requirements.txt to make sure everything works properly):

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
| Fake useragent | https://github.com/fake-useragent/fake-useragent |
| SQL Alchemy | https://www.sqlalchemy.org/ |

Make sure to install the required libraries before running the Match Predictor.


## Acknowledgements

- The Match Predictor utilizes the scikit-learn and XGBoost libraries for machine learning models.
- It uses the pandas and numpy libraries to organize data and the bs4, and requests library to scrape the data.
- The data used in the predictor is sourced from FBREF (https://fbref.com/).
