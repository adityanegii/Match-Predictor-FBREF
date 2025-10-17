import time
from flask import Flask, jsonify
from flask_cors import CORS
import csv
from main import scrape, train_and_predict
from database import init_db, SessionLocal
from data_models.Result import Result
from constants import league_full
from sqlalchemy.exc import SQLAlchemyError

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
    # try:
    #     filepath = f"data/predictions_{model}_{league}.csv"
    #     with open(filepath) as f:
    #         csv_data = list(csv.DictReader(f))
    #     return jsonify(csv_data)
    # except FileNotFoundError:
    #     return jsonify({"error": f"No data found for {model} - {league}"}), 404

    # Get latest (only today or later) Results from database
    # session = SessionLocal()
    # results = session.query(Result).filter(Result.league == league_full[league], Result.model_type == model, Result.date >= time.strftime("%Y-%m-%d")).all()
    # session.close()

    # if results:
    #     return jsonify([result.as_dict() for result in results])
    # else:
    #     return jsonify({"error": f"No results found for {model} - {league}"}), 404

    try:
        session = SessionLocal()
        
        # Validate league and model inputs
        if league not in league_full or model not in ["RFC", "XGBC", "RFR", "XGBR", "SVC_1v1", "LR_1v1", "Ensemble"]:
            return jsonify({"error": f"Invalid league or model: {league} - {model}"}), 400

        results = (
            session.query(Result)
            .filter(
                Result.league == league_full[league],
                Result.model_type == model,
                Result.date >= time.strftime("%Y-%m-%d")
            )
            .all()
        )

        session.close()

        if results:
            return jsonify([r.as_dict() for r in results])
        else:
            # No data, instruct to scrape/train
            return jsonify({
                "message": f"No results found for {model} - {league}. Please run scrape/train."
            }), 200

    except SQLAlchemyError as e:
        # Database-related errors
        return jsonify({
            "error": "Database error occurred.",
            "details": str(e)
        }), 500

    except Exception as e:
        # Catch-all for unexpected issues
        return jsonify({
            "error": "Unexpected server error.",
            "details": str(e)
        }), 404


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