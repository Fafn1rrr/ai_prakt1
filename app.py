from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/options")
def options():
    return render_template("options.html")


if __name__ == "__main__":
    app.run(debug=True)