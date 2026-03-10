from flask import Flask, render_template, request, redirect, url_for, session
import random
import math
import copy

app = Flask(__name__)
app.secret_key = "change-me-please"

# Чтобы не висло на каждом клике (потом увеличишь)
MINIMAX_DEPTH = 2
ALPHABETA_DEPTH = 3




class GameState:
    def __init__(self, numbers, turn, algorithm, human_points=0, ai_points=0):
        self.numbers = numbers
        self.human_points = human_points
        self.ai_points = ai_points
        self.turn = turn          # True = human, False = ai
        self.algorithm = algorithm # True = minimax, False = alpha-beta

    def is_finish(self):
        return len(self.numbers) == 0

    def switch_turn(self):
        self.turn = not self.turn


def minimax(state, depth):
    if state.is_finish():
        return (state.ai_points - state.human_points, None)

    if depth == 0:
        return (heuristic(state), None)

    moves = generate_moves(state)

    if not state.turn:  # AI MAX
        best_value = -math.inf
        best_move = None
        for move, idx in moves:
            child = copy.deepcopy(state)
            child = apply_move(child, move, idx)
            value, _ = minimax(child, depth - 1)
            if value > best_value:
                best_value = value
                best_move = (move, idx)
        return (best_value, best_move)

    else:  # Human MIN
        best_value = math.inf
        best_move = None
        for move, idx in moves:
            child = copy.deepcopy(state)
            child = apply_move(child, move, idx)
            value, _ = minimax(child, depth - 1)
            if value < best_value:
                best_value = value
                best_move = (move, idx)
        return (best_value, best_move)


def alpha_beta(state, depth, alpha=-math.inf, beta=math.inf):
    if state.is_finish():
        return (state.ai_points - state.human_points, None)

    if depth == 0:
        return (heuristic(state), None)

    moves = generate_moves(state)

    if not state.turn:  # AI MAX
        best_value = -math.inf
        best_move = None
        for move, idx in moves:
            child = copy.deepcopy(state)
            child = apply_move(child, move, idx)
            value, _ = alpha_beta(child, depth - 1, alpha, beta)

            if value > best_value:
                best_value = value
                best_move = (move, idx)

            alpha = max(alpha, best_value)
            if beta <= alpha:
                break
        return (best_value, best_move)

    else:  # Human MIN
        best_value = math.inf
        best_move = None
        for move, idx in moves:
            child = copy.deepcopy(state)
            child = apply_move(child, move, idx)
            value, _ = alpha_beta(child, depth - 1, alpha, beta)

            if value < best_value:
                best_value = value
                best_move = (move, idx)

            beta = min(beta, best_value)
            if beta <= alpha:
                break
        return (best_value, best_move)


def take(state, index):
    return state.numbers.pop(index)


def split2(state, index):
    state.numbers.pop(index)
    state.numbers.insert(index, 1)
    state.numbers.insert(index, 1)
    return state


def split4(state, index):
    state.numbers.pop(index)
    state.numbers.insert(index, 2)
    state.numbers.insert(index, 2)
    return state


def apply_move(state, move, index):
    if index < 0 or index >= len(state.numbers):
        return state

    if move == "take":
        value = take(state, index)
        if state.turn:
            state.human_points += value
        else:
            state.ai_points += value

    elif move == "split2":
        if state.numbers[index] != 2:
            return state
        split2(state, index)
        # split2: +1 point to opponent
        if state.turn:
            state.ai_points += 1
        else:
            state.human_points += 1

    elif move == "split4":
        if state.numbers[index] != 4:
            return state
        split4(state, index)
        # split4: -1 point from opponent
        if state.turn:
            state.ai_points -= 1
        else:
            state.human_points -= 1

    state.switch_turn()
    return state


def ai_move(state):
    # IMPORTANT: возвращаем state, чтобы нигде не превратить его в None
    if state.algorithm:  # minimax
        _, move = minimax(state, depth=MINIMAX_DEPTH)
    else:               # alpha-beta
        _, move = alpha_beta(state, depth=ALPHABETA_DEPTH)

    if move is None:
        return state

    action, index = move
    apply_move(state, action, index)
    return state

def ai_do_turn_and_get_text(state):
    # вычисляем лучший ход так же, как ai_move
    if state.algorithm:  # minimax
        _, move = minimax(state, depth=MINIMAX_DEPTH)
    else:                # alpha-beta
        _, move = alpha_beta(state, depth=ALPHABETA_DEPTH)

    if move is None:
        return None

    action, index = move

    # для красоты можно показать и число, которое было выбрано
    chosen = state.numbers[index] if 0 <= index < len(state.numbers) else None

    apply_move(state, action, index)

    if chosen is None:
        return f"{action} (index {index})"
    return f"{action} {chosen} (index {index})"

def heuristic(state):
    a = 3
    b = 2
    return a * (state.ai_points - state.human_points) + b * (
        4 * count(state, 4) + 3 * count(state, 3) + 3 * count(state, 2) + count(state, 1)
    )


def count(state, value):
    cnt = 0
    for i in state.numbers:
        if i == value:
            cnt += 1
    return cnt


def generate_moves(state):
    moves = []
    for i in range(len(state.numbers)):
        moves.append(("take", i))
        if state.numbers[i] == 2:
            moves.append(("split2", i))
        if state.numbers[i] == 4:
            moves.append(("split4", i))
    return moves



def generate_numbers(length):
    return [random.randint(1, 4) for _ in range(length)]


def make_state_from_session(d):
    return GameState(
        numbers=d["numbers"],
        turn=d["turn_bool"],
        algorithm=d["algo_bool"],
        human_points=d["human_points"],
        ai_points=d["ai_points"]
    )


def save_state_to_session(state, meta):
    session["game_view"] = {
        "length": meta["length"],
        "starter": meta["starter"],   # "human"/"ai" display
        "algo": meta["algo"],         # "minimax"/"alphabeta" display
        "numbers": state.numbers,
        "human_points": state.human_points,
        "ai_points": state.ai_points,
        "turn_bool": state.turn,      # bool
        "algo_bool": state.algorithm,  # bool
        "last_ai_move": meta.get("last_ai_move")
    }
    session.modified = True  # важно для стабильности сохранения


def calc_winner(state):
    if not state.is_finish():
        return None
    if state.ai_points > state.human_points:
        return "AI"
    if state.ai_points < state.human_points:
        return "Human"
    return "Draw"



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/options", methods=["POST"])
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
        if length < 15 or length > 20:
            return redirect(url_for("index"))

        starter = request.form.get("starter", "human")   # human/ai
        algo_str = request.form.get("algo", "minimax")   # minimax/alphabeta

        turn_bool = (starter == "human")
        algo_bool = (algo_str == "minimax")

        state = GameState(numbers=generate_numbers(length), turn=turn_bool, algorithm=algo_bool)
        meta = {"length": length, "starter": starter, "algo": algo_str}

        # если первым ходит AI — ход AI
        if (not state.turn) and (not state.is_finish()):
            meta["last_ai_move"] = ai_do_turn_and_get_text(state)

        save_state_to_session(state, meta)
        return redirect(url_for("game"))

    data = session.get("game_view")
    if not data:
        return redirect(url_for("index"))

    state = make_state_from_session(data)
    finished = state.is_finish()
    winner = calc_winner(state)

    return render_template(
        "game.html",
        length=data["length"],
        starter=data["starter"],
        algo=data["algo"],
        numbers=state.numbers,
        human_points=state.human_points,
        ai_points=state.ai_points,
        turn=("human" if state.turn else "ai"),
        finished=finished,
        winner=winner,
        last_ai_move=data.get("last_ai_move")
    )


@app.route("/move", methods=["POST"])
def move():
    data = session.get("game_view")
    if not data:
        return redirect(url_for("index"))

    state = make_state_from_session(data)

    if state.is_finish():
        return redirect(url_for("game"))

    # кнопки доступны только человеку, но на всякий случай
    if not state.turn:
        return redirect(url_for("game"))

    index_str = request.form.get("index", "").strip()
    action = request.form.get("action", "").strip()

    if (not index_str.isdigit()) or (action not in ("take", "split2", "split4")):
        return redirect(url_for("game"))

    idx = int(index_str)

    # ход человека
    apply_move(state, action, idx)

    meta = {"length": data["length"], "starter": data["starter"], "algo": data["algo"]}
    # если теперь ход AI — ход AI
    if (not state.is_finish()) and (not state.turn):
        meta["last_ai_move"] = ai_do_turn_and_get_text(state)

    save_state_to_session(state, meta)

    return redirect(url_for("game"))


@app.route("/restart")
def restart():
    data = session.get("game_view")
    if not data:
        return redirect(url_for("index"))

    length = data["length"]
    starter = data["starter"]
    algo_str = data["algo"]

    turn_bool = (starter == "human")
    algo_bool = (algo_str == "minimax")

    state = GameState(numbers=generate_numbers(length), turn=turn_bool, algorithm=algo_bool)
    meta = {"length": length, "starter": starter, "algo": algo_str, "last_ai_move": None}

    if (not state.turn) and (not state.is_finish()):
        meta["last_ai_move"] = ai_do_turn_and_get_text(state)

    save_state_to_session(state, meta)
    return redirect(url_for("game"))


if __name__ == "__main__":
    app.run(debug=True)