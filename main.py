import numpy as np

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

def human_move(state):
    moves = generate_moves(state)
    for i in range(len(moves)):
        print(i, " ", moves[i]) 
    while True:
        try:
            choice = int(input("Choose move number: "))
            action, index = moves[choice]
            if action == "take":
                value = take(state, index)
                state.human_points = state.human_points + value

            elif action == "split2":
                split2(state, index)
                state.ai_points += 1

            elif action == "split4":
                split4(state, index)
                state.ai_points -= 1
            state.switch_turn()
            break
        except Exception as e:
            print(e)

def ai_move(state):
    print("AI not working now")  
    state.switch_turn()      

def generate_moves(state):
    moves = []
    for i in range(len(state.numbers)):
        moves.append(("take",i))
        if state.numbers[i] == 2:
            moves.append(("split2",i))
        if state.numbers[i] == 4:
            moves.append(("split4",i))    
    return moves
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

def GameStart(numbers):
    newGame = GameState(numbers)
    print("Game started!")
    while not newGame.is_finish():
        newGame.print_state()
        if newGame.turn:
            human_move(newGame)
        else:
            ai_move(newGame)

length = user_input()
if length is not None:
    GameStart(length)