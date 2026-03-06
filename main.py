import numpy as np
import copy
import math

# Datu struktūra
class GameState:
    def __init__(self, numbers,human_points = 0, ai_points=0):
        self.numbers = numbers
        self.human_points = human_points
        self.ai_points = ai_points
        self.turn = bool #true = human turn, false = ai_turn
    def is_finish(self):
        return len(self.numbers) == 0
    def print_state(self):
        print("Numbers : ", self.numbers)
        print("Human points: ", self.human_points)
        print("AI points: ",self.ai_points)
        if self.turn:
            print("Human turn")
        else: print("AI turn")
    def switch_turn(self):
        self.turn = not self.turn    
        
# Algoritmi
def heuristic(state):
   a = 0.5 # a,b - koeficienti heiristiskajai funkcijai, tos var brīvi mainīt, galvenais, lai summa būtu 1.
   b = 0.5
    return a*(state.ai_points - state.human_points) + b*(4*count(state,4) + 3*count(state,3) + 2*count(state,2) + count(state,1))

def minimax(state, depth):
        """
    Funkcija realizē minimax algoritmu.
    
    Tā atgriež:
    best_value – labāko novērtējumu (stāvokļa vērtību)
    best_move – labāko gājienu (piemēram ("take", i), ("split2", i), ("split4", i))

    depth – cik dziļi tiek pārmeklēts spēles koks.
    """

    # Ja spēle ir beigusies (virkne tukša),
    # tad aprēķinām precīzu rezultātu: AI punkti - cilvēka punkti.
    # Šī ir terminālā virsotne spēles kokā.
    if state.is_finish():
        return (state.ai_points - state.human_points, None)

    # dziļuma ierobežojums: evristika
    if depth == 0:
        return (heuristic(state), None)

    moves = generate_moves(state)   # Ģenerējam visus iespējamos gājienus no pašreizējā stāvokļa.

    # AI gājiens, kad state.turn == False -> maksimizācija
    if not state.turn:
        best_value = -math.inf
        best_move = None

        for move, idx in moves:
            child = copy.deepcopy(state)
            child = apply_move(child, move, idx)      # svarīgi: maina stāvokli un pārslēdz gājienu
            value, _ = minimax(child, depth - 1)

            if value > best_value:
                best_value = value
                best_move = (move, idx)

        return (best_value, best_move)

    # Cilvēka gājiens, kad state.turn == True -> minimizācija
    else:
        best_value = math.inf
        best_move = None

        for move, idx in moves:
            child = copy.deepcopy(state)
            child = apply_move(child, move, idx)
            value, _ = minimax(child, depth - 1)

            if value < best_value:
                best_value = value
                best_move = (move, idx)

        return (best_value, best_move)         # Atgriežam minimālo vērtību un atbilstošo gājienu

def alpha_beta(state, depth, alpha=-math.inf, beta=math.inf):
    """
    Funkcija realizē minimax algoritmu ar alpha-beta atzarošanu.

    Tā atgriež:
    best_value – labāko novērtējumu (stāvokļa vērtību)
    best_move – labāko gājienu (piemēram ("take", i), ("split2", i), ("split4", i))

    depth – cik dziļi tiek pārmeklēts spēles koks
    alpha – labākā (lielākā) vērtība, ko līdz šim garantē MAX spēlētājs
    beta – labākā (mazākā) vērtība, ko līdz šim garantē MIN spēlētājs
    """
    # Ja spēle ir beigusies (virkne tukša),
    # tad aprēķinām precīzu rezultātu: AI punkti - cilvēka punkti.
    # Šī ir terminālā virsotne spēles kokā.
    if state.is_finish():
        return (state.ai_points - state.human_points, None)
    # Ja esam sasnieguši maksimālo pārmeklēšanas dziļumu,
    # izmantojam evristisko funkciju, lai novērtētu stāvokli.
    if depth == 0:
        return (heuristic(state), None)
    # Ģenerējam visus iespējamos gājienus no pašreizējā stāvokļa
    moves = generate_moves(state)
    # AI gājiens (MAX spēlētājs)
    if not state.turn:
        best_value = -math.inf   # sākam ar ļoti mazu vērtību
        best_move = None
        # Izskatām visus iespējamos gājienus
        for move, idx in moves:
            # Izveidojam bērna stāvokli (spēles kopiju)
            child = copy.deepcopy(state)
            # Pielietojam gājienu un pārslēdzam spēlētāju
            child = apply_move(child, move, idx)
            # Rekursīvi izsaucam alpha-beta nākamajam dziļumam
            value, _ = alpha_beta(child, depth - 1, alpha, beta)
            # Ja atrastā vērtība ir labāka par pašreizējo,
            # saglabājam to kā labāko gājienu
            if value > best_value:
                best_value = value
                best_move = (move, idx)
            # Atjauninām alpha vērtību
            # alpha glabā labāko MAX rezultātu līdz šim
            alpha = max(alpha, best_value)
            # Alpha-beta atzarošana:
            # ja beta <= alpha, tālākos zarus nav jēgas skatīt,
            # jo pretinieks šo zaru nekad neizvēlēsies
            if beta <= alpha:
                break
        # Atgriežam labāko atrasto vērtību un gājienu
        return (best_value, best_move)
    # Cilvēka gājiens (MIN spēlētājs)
    else:
        best_value = math.inf    # sākam ar ļoti lielu vērtību
        best_move = None
        # Izskatām visus iespējamos gājienus
        for move, idx in moves:
            # Izveidojam bērna stāvokļa kopiju
            child = copy.deepcopy(state)
            # Pielietojam gājienu
            child = apply_move(child, move, idx)
            # Rekursīvs izsaukums nākamajam dziļumam
            value, _ = alpha_beta(child, depth - 1, alpha, beta)
            # Ja atrastā vērtība ir mazāka par pašreizējo,
            # saglabājam to kā labāko (MIN izvēlas mazāko)
            if value < best_value:
                best_value = value
                best_move = (move, idx)
            # Atjauninām beta vērtību
            # beta glabā labāko MIN rezultātu līdz šim
            beta = min(beta, best_value)
            # Alpha-beta atzarošana
            # ja beta <= alpha, pārtraucam šī zara izskatīšanu
            if beta <= alpha:
                break
        # Atgriežam minimālo vērtību un atbilstošo gājienu
        return (best_value, best_move)
# Iespējamie gājieni
def take(state,index):
    return state.numbers.pop(index)
    
def split2(state,index):
    state.numbers.pop(index)
    state.numbers.insert(index, 1)
    state.numbers.insert(index, 1)
    return state

def split4(state,index):
    state.numbers.pop(index)
    state.numbers.insert(index, 2)
    state.numbers.insert(index, 2)
    return state

def generate_moves(state):
    moves = []
    for i in range(len(state.numbers)):
        moves.append(("take",i))
        if state.numbers[i] == 2:
            moves.append(("split2",i))
        if state.numbers[i] == 4:
            moves.append(("split4",i))    
    return moves

def apply_move(state, move, index): # Izveidoju kā atsevišķu funkciju, lai nerakstītu kodu divreiz. Gājiens tiek pārslēgts šīs funkcijas beigās.
    if move == "take":
        value = take(state, index)
        if state.turn:
            state.human_points = state.human_points + value
        else:
            state.ai_points = state.ai_points + value
    elif move == "split2":
        split2(state, index)
        if state.turn:
            state.ai_points += 1
        else:
            state.human_points += 1
    elif move == "split4":
        split4(state, index)
        if state.turn:
            state.ai_points -= 1
        else:
            state.human_points -= 1
    state.switch_turn()
    return state                

# Spēlētāja gājiens
def human_move(state):
    moves = generate_moves(state)
    for i in range(len(moves)):
        print(i, " ", moves[i]) 
    while True: # Cikls ir nepieciešams, lai lietotājs varētu atkārtoti ievadīt gājiena numuru, ja tiek ievadīta kļūdaina vērtība
        try:
            choice = int(input("Choose move number: "))
            move = moves[choice]
            state = apply_move(state, move[0], move[1])
            break
        except Exception as e:
            print(e)
# Datora gājiens
def ai_move(state):
    print("AI not working now")  
    state.switch_turn() 

# Input
def user_input():
    try:
        length = int(input("please write length of the numbers from 15 to 20: \n"))
        if length not in range(15,21):
            print("Length must be between 15 and 20")
            return
        numbers = np.random.randint(1,5,size = length).tolist()
        print(numbers)
        return numbers
    except Exception as e:
        print(e)
# Spēles pamata loģika
def GameStart(numbers):
    newGame = GameState(numbers)
    print("Game started!")
    while not newGame.is_finish():
        newGame.print_state()
        if newGame.turn:
            human_move(newGame)
        else:
            ai_move(newGame)
# main
length = user_input()
if length is not None:
    GameStart(length)



