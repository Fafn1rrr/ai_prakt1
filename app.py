from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "change-me-please"


def generate_numbers(length):
    return [random.randint(1, 4) for _ in range(length)]


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

    return render_template("options.html", length=length, error=None)


@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        length_str = request.form.get("length", "").strip()
        if not length_str.isdigit():
            return redirect(url_for("index"))
        length = int(length_str)

        starter = request.form.get("starter", "human")
        algo = request.form.get("algo", "minimax")

        session["game_view"] = {
            "length": length,
            "starter": starter,
            "algo": algo,
            "numbers": generate_numbers(length)
        }

        return redirect(url_for("game"))

    data = session.get("game_view")
    if not data:
        return redirect(url_for("index"))

    return render_template(
        "game.html",
        length=data["length"],
        starter=data["starter"],
        algo=data["algo"],
        numbers=data["numbers"]
    )


@app.route("/restart")
def restart():
    data = session.get("game_view")
    if not data:
        return redirect(url_for("index"))

    length = data["length"]
    data["numbers"] = generate_numbers(length)
    session["game_view"] = data
    return redirect(url_for("game"))


if __name__ == "__main__":
    app.run(debug=True)