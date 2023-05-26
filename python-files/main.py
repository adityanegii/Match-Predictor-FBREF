import data_processor as DP
import scraper
import RandomForest as RF
import pandas as pd

def scrape(years, url): 
    return scraper.scrape(years, url)

def process(df):
    return DP.combine(DP.get_overall_averages(DP.clean_data(df)))

def train(data, predictors, rf):
    RF.evaluate_model(RF.train(data.dropna(), predictors, rf))

def predict(data, predictors, rf):
    RF.predict(data, predictors, rf).to_csv("predictions.csv", index=False)

def main():
    # Scrape Data
    years = list(range(2022, 2020, - 1))
    url = "https://fbref.com/en/comps/9/Premier-League-Stats"
    # matches_df = scrape(years, url)

    matches_df = pd.read_csv("matches.csv")

    # Process Data
    data = process(matches_df)
    # Train and predict
    predictors, rf = RF.initialize()
    print("------------------TRAINING------------------")
    train(data, predictors, rf)
    print("------------------PREDICTING------------------")
    print(data['date'].dtype)
    next_games = data[data['date'].dt.date >= pd.Timestamp.now().date()]
    print(predict(next_games, predictors, rf))

main()