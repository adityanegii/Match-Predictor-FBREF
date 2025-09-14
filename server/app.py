import time
from flask import Flask, jsonify
from flask_cors import CORS
import csv
from main import scrape, train_and_predict
from database import init_db

def create_app():
    app = Flask(__name__)
    CORS(app)

    with app.app_context():
        init_db()
    
    return app

app = create_app()


@app.route("/api/<league>/<model>", methods=['GET'])
def get_predictions(league, model):
    """
    league: ENG1, FRA1, GER1, ITA1, SPA1
    model: RFC, XGBC, RFR, XGBR, SVC, LR, Ensemble
    """
    try:
        filepath = f"data/predictions_{model}_{league}.csv"
        with open(filepath) as f:
            csv_data = list(csv.DictReader(f))
        return jsonify(csv_data)
    except FileNotFoundError:
        return jsonify({"error": f"No data found for {model} - {league}"}), 404

@app.route("/api/train-and-predict")
def predict():
    try:
        train_and_predict()
        return jsonify({"message": "OK"})
    except Exception as e:
        return jsonify({"message": f"Error {e}"})

@app.route("/api/scrape")
def scrape_data():
    try:
        scrape()
        return jsonify({"message": "OK"})
    except Exception as e:
        print(e)
        return jsonify({"message": f"Error {e}"})


@app.route("/api/test")
def test():
    try:
        time.sleep(5)
        return jsonify({"message": "Test OK"})
    except Exception as e:
        print(e)
        return jsonify({"message": f"Error {e}"})

if __name__ == "__main__":
    app.run(debug=True, port=8080)