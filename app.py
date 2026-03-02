from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/options", methods=["GET", "POST"])
def options():
    length_str = request.form.get("length", "").strip()

    if not length_str.isdigit():
        return render_template("index.html", error="Ievadi skaitli no 15 līdz 20!")

    length = int(length_str)
    if length < 15 or length > 20:
        return render_template("index.html", error="Garumam jābūt 15..20!")

    return render_template("options.html", length=length)


if __name__ == "__main__":
    app.run(debug=True)