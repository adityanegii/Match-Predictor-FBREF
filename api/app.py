from flask import Flask

app = Flask(__name__)

@app.route('/'):
def check():
    return 'Flask is running!'