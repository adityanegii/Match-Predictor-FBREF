from flask import Flask, jsonify
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)

@app.route("/api/E0/RFC", methods=['GET'])
def get_pl_rfc():
    with open("data/predictions_RFC.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)


@app.route("/api/E0/XGBC", methods=['GET'])
def get_pl_xgbc():
    with open("data/predictions_XGBC.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/E0/RFR", methods=['GET'])
def get_pl_rfr():
    with open("data/predictions_RFR.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

@app.route("/api/E0/XGBR", methods=['GET'])
def get_pl_xgbr():
    with open("data/predictions_XGBR.csv") as f:
        csv_data = list(csv.DictReader(f))

    return jsonify(csv_data)

if __name__ == "__main__":
    app.run(debug=True, port=8080)