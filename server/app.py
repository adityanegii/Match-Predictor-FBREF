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

@app.route("/api/ENG1/RFC", methods=['GET'])
def get_pl_rfc():
    with open("data/predictions_RFC_ENG1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/ENG1/XGBC", methods=['GET'])
def get_pl_xgbc():
    with open("data/predictions_XGBC_ENG1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/ENG1/RFR", methods=['GET'])
def get_pl_rfr():
    with open("data/predictions_RFR_ENG1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/ENG1/XGBR", methods=['GET'])
def get_pl_xgbr():
    with open("data/predictions_XGBR_ENG1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/FRA1/RFC", methods=['GET'])
def get_l1_rfc():
    with open("data/predictions_RFC_FRA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/FRA1/XGBC", methods=['GET'])
def get_l1_xgbc():
    with open("data/predictions_XGBC_FRA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/FRA1/RFR", methods=['GET'])
def get_l1_rfr():
    with open("data/predictions_RFR_FRA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/FRA1/XGBR", methods=['GET'])
def get_l1_xgbr():
    with open("data/predictions_XGBR_FRA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)    

@app.route("/api/GER1/RFC", methods=['GET'])
def get_bl_rfc():
    with open("data/predictions_RFC_GER1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)    

@app.route("/api/GER1/XGBC", methods=['GET'])
def get_bl_xgbc():
    with open("data/predictions_XGBC_GER1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)    

@app.route("/api/GER1/RFR", methods=['GET'])
def get_bl_rfr():
    with open("data/predictions_RFR_GER1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/GER1/XGBR", methods=['GET'])
def get_bl_xgbr():
    with open("data/predictions_XGBR_GER1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/ITA1/RFC", methods=['GET'])
def get_sa_rfc():
    with open("data/predictions_RFC_ITA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/ITA1/XGBC", methods=['GET'])
def get_sa_xgbc():
    with open("data/predictions_XGBC_ITA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/ITA1/RFR", methods=['GET'])
def get_sa_rfr():
    with open("data/predictions_RFR_ITA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/ITA1/XGBR", methods=['GET'])
def get_sa_xgbr():
    with open("data/predictions_XGBR_ITA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/SPA1/RFC", methods=['GET'])
def get_pd_rfc():
    with open("data/predictions_RFC_SPA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/SPA1/XGBC", methods=['GET'])
def get_pd_xgbc():
    with open("data/predictions_XGBC_SPA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/SPA1/RFR", methods=['GET'])
def get_pd_rfr():
    with open("data/predictions_RFR_SPA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/SPA1/XGBR", methods=['GET'])
def get_pd_xgbr():
    with open("data/predictions_XGBR_SPA1.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

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
        return jsonify({"message": f"Error {e}"})


@app.route("/api/test")
def test():
    try:
        time.sleep(5)
        return jsonify({"message": "Test OK"})
    except Exception as e:
        return jsonify({"message": f"Error {e}"})

if __name__ == "__main__":
    app.run(debug=True, port=8080)