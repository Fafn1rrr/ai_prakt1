from flask import Flask, render_template, request, redirect, url_for, session
import random
import math
import time     

app = Flask(__name__)
app.secret_key = "change-me-please"

MINIMAX_DEPTH = 5
ALPHABETA_DEPTH = 8

PRINT_AI_STATS = True  


class Node:
    def __init__(self, numbers, turn, algorithm, human_points, ai_points, move_desc=""):
        self.numbers = sorted(numbers)
        self.human_points = human_points
        self.ai_points = ai_points
        self.turn = turn          
        self.algorithm = algorithm 
        self.children = [] 
        self.move_desc = move_desc 
        self.value = None 

         
    def is_finish(self):
        return len(self.numbers) == 0
    
      
    def generate_children(self):
        moves = [] 
        unique_numbers = set(self.numbers) 
        
        take_points = {
            1: 1,
            2: 1,
            3: 3,
            4: 2 
        }       

        for num in unique_numbers:
            new_seq = self.numbers.copy() 
            new_seq.remove(num)  
            gained = take_points[num] 
            if self.turn:  
                moves.append(Node(new_seq, False, self.algorithm, self.human_points + gained, self.ai_points, move_desc = f"Human took {num}"))
            else:           
                moves.append(Node(new_seq, True, self.algorithm, self.human_points, self.ai_points + gained, move_desc = f"AI took {num}"))
        if 2 in self.numbers:
            new_seq = self.numbers.copy()
            new_seq.remove(2)
            new_seq.extend([1, 1])
            if self.turn:  
                moves.append(Node(new_seq, False, self.algorithm, self.human_points + 0 , self.ai_points - 1, move_desc = f"Human split 2"))
            else:           
                moves.append(Node(new_seq, True, self.algorithm, self.human_points - 1 , self.ai_points + 0, move_desc = f"AI split 2"))                    
        if 4 in self.numbers:
            new_seq = self.numbers.copy()
            new_seq.remove(4)
            new_seq.extend([2, 2])
            if self.turn:  
                moves.append(Node(new_seq, False, self.algorithm, self.human_points + 2, self.ai_points, move_desc = f"Human split 4"))
            else:           
                moves.append(Node(new_seq, True, self.algorithm, self.human_points, self.ai_points + 2, move_desc = f"AI split 4"))
        self.children = moves 
        return moves 
def make_stats():
    return {
        "calls": 0,   
        "leaves": 0,   
        "generated_nodes": 0 
     }
def heuristic(node):
    if node.is_finish():
        return 10000 * (node.ai_points - node.human_points)

    score_diff = node.ai_points - node.human_points
    c1 = node.numbers.count(1)
    c2 = node.numbers.count(2)
    c3 = node.numbers.count(3)
    c4 = node.numbers.count(4)

    side = 1 if not node.turn else -1
    
    return (
        10 * score_diff +
        side * (0.5 * c1 + 1.0 * c2 + 1.5 * c3 + 2.0 * c4)
    )
    
def minimax(node, depth, stats=None):
    if stats is not None:
        stats["calls"] += 1
    if depth == 0 or node.is_finish(): 
        if stats is not None:
            stats["leaves"] += 1
        return heuristic(node), None
    children = node.generate_children()

    if stats is not None:
        stats["generated_nodes"] += len(children)

    if not node.turn:  
        best_value = -math.inf 
        best_node = None 
        for child in children: 
            value, _ = minimax(child, depth - 1, stats) 
            if value > best_value:  
                best_value = value 
                best_node = child 
        return best_value, best_node 

    else:  
        best_value = math.inf
        best_node = None
        for child in children:
            value, _ = minimax(child, depth - 1, stats)
            if value < best_value:
                best_value = value
                best_node = child
        return best_value, best_node

def alpha_beta(node, depth, alpha=-math.inf, beta=math.inf, stats=None):
    if stats is not None:
        stats["calls"] += 1
    if depth == 0 or node.is_finish():
        if stats is not None:
            stats["leaves"] += 1
        return heuristic(node), None
    
    children = node.generate_children()
    if stats is not None:
        stats["generated_nodes"] += len(children)

    if not node.turn:  
        best_value = -math.inf
        best_node = None
        for child in children:
            value, _ = alpha_beta(child, depth - 1, alpha, beta, stats)

            if value > best_value:
                best_value = value
                best_node = child

            alpha = max(alpha, best_value) 
            if beta <= alpha:
                break  
        return best_value, best_node

    else:  
        best_value = math.inf
        best_node = None
        for child in children:
            value, _ = alpha_beta(child, depth - 1, alpha, beta, stats)

            if value < best_value:
                best_value = value
                best_node = child

            beta = min(beta, best_value)
            if beta <= alpha:
                break
        return best_value, best_node

def ai_do_turn_and_get_text(node):
    stats = make_stats()
    start_time = time.perf_counter()
    
    if node.algorithm:
        best_value, best_node = minimax(node, depth=MINIMAX_DEPTH, stats=stats)
        algo_name = "Minimax"
    else:
        best_value, best_node = alpha_beta(node, depth=ALPHABETA_DEPTH, stats=stats)
        algo_name = "Alpha-Beta"
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    if PRINT_AI_STATS:
        print(
            f"[{algo_name}] "
            f"move={best_node.move_desc if best_node else 'None'} | "
            f"value={best_value} | "
            f"time={elapsed_ms:.3f} ms | "
            f"calls={stats['calls']} | "
            f"leaves={stats['leaves'] }"
            f"generated_nodes={stats['generated_nodes'] }",
            flush=True
        )
    if best_node is None:
        return node, None, stats["generated_nodes"], elapsed_ms
    return best_node, best_node.move_desc, stats["generated_nodes"], elapsed_ms

def generate_numbers(length):
    return [random.randint(1, 4) for _ in range(length)]

def make_state_from_session(d):
    return Node(
        numbers=d["numbers"],
        turn=d["turn_bool"],
        algorithm=d["algo_bool"],
        human_points=d["human_points"],
        ai_points=d["ai_points"]
    )

def save_state_to_session(state, meta):
    session["game_view"] = {
        "length": meta["length"],
        "starter": meta["starter"],   
        "algo": meta["algo"],         
        "numbers": state.numbers,
        "human_points": state.human_points,
        "ai_points": state.ai_points,
        "turn_bool": state.turn,      
        "algo_bool": state.algorithm,  
        "last_ai_move": meta.get("last_ai_move"),
        "nodes_count": meta.get("nodes_count"),
        "time_ms": meta.get("time_ms")
    }
    session.modified = True  

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

@app.route("/game", methods=["GET", "POST"])
def game():
    if request.method == "POST":
        length_str = request.form.get("length", "").strip()

        if not length_str.isdigit():
            return render_template("index.html", error="Ievadi skaitli no 15 līdz 20!")

        length = int(length_str)
        if length < 15 or length > 20:
            return render_template("index.html", error="Garumam jābūt 15..20!")

        starter = request.form.get("starter", "human") 
        algo_str = request.form.get("algo", "minimax")   

        turn_bool = (starter == "human")
        algo_bool = (algo_str == "minimax")
        node = Node(numbers=generate_numbers(length), turn=turn_bool,human_points=0, ai_points=0, algorithm=algo_bool)
        meta = {"length": length, "starter": starter, "algo": algo_str, "last_ai_move": None, "generated_nodes": None, "visited_nodes": None, "leaf_nodes": None, "time_ms": None}

        
        if not node.turn and not node.is_finish():
            node, text, generated_nodes, elapsed_ms = ai_do_turn_and_get_text(node)
            meta["last_ai_move"] = text
            meta["nodes_count"] = generated_nodes
            meta["time_ms"] = elapsed_ms

        save_state_to_session(node, meta)
        return redirect(url_for("game"))

    data = session.get("game_view")
    if not data:
        return redirect(url_for("index"))

    node = make_state_from_session(data)
    finished = node.is_finish()
    winner = calc_winner(node)
    moves = []
    mapped_moves = {}

    if node.turn and not finished:
        moves = node.generate_children()

    for idx, m in enumerate(moves):
        mapped_moves[m.move_desc] = idx

        
    return render_template(
        "game.html",
        length=data["length"],
        starter=data["starter"],
        algo=data["algo"],
        numbers=node.numbers,
        mapped_moves=mapped_moves,
        human_points=node.human_points,
        ai_points=node.ai_points,
        turn=("human" if node.turn else "ai"),
        finished=finished,
        winner=winner,
        last_ai_move=data.get("last_ai_move"),
        nodes_count=data.get("nodes_count"),
        time_ms=data.get("time_ms")
    )

@app.route("/move", methods=["POST"])
def move():
    data = session.get("game_view")
    if not data:
        return redirect(url_for("index"))

    node = make_state_from_session(data)

    if node.is_finish():
        return redirect(url_for("game"))
    
    if not node.turn:
        return redirect(url_for("game"))
    
    move_id_str = request.form.get("move_id")

    if move_id_str is None or not move_id_str.isdigit():
        return redirect(url_for("game"))

    move_id = int(move_id_str)

    children = node.generate_children()
    node = children[move_id]


    meta = {"length": data["length"], "starter": data["starter"], "algo": data["algo"], "last_ai_move": None, "generated_nodes": None, "visited_nodes": None, "leaf_nodes": None, "time_ms": None}
    
    if (not node.is_finish()) and (not node.turn):
        node, text, generated_nodes, elapsed_ms = ai_do_turn_and_get_text(node)
        meta["last_ai_move"] = text
        meta["nodes_count"] = generated_nodes
        meta["time_ms"] = elapsed_ms
    save_state_to_session(node, meta)

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
    
    node = Node(numbers=generate_numbers(length), turn=turn_bool,human_points=0, ai_points=0, algorithm=algo_bool)
    meta = {"length": length, "starter": starter, "algo": algo_str, "last_ai_move": None, "generated_nodes": None, "visited_nodes": None, "leaf_nodes": None, "time_ms": None}

    if (not node.turn) and (not node.is_finish()):
        node, text, generated_nodes, elapsed_ms = ai_do_turn_and_get_text(node)
        meta["last_ai_move"] = text
        meta["nodes_count"] = generated_nodes
        meta["time_ms"] = elapsed_ms

    save_state_to_session(node, meta)
    return redirect(url_for("game"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
