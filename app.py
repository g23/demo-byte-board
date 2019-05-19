from flask import Flask

from db import get_db, close_db

app = Flask(__name__)

@app.route("/")
def hello():
    test()
    return "Hello world from Flask!"
