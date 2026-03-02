import numpy as np

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

def minimax():
    return 0

def alpha_beta():
    return 0
    
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

