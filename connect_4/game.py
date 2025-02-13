import requests
import threading
import random

key = "adc0713c-b3bc-4454-ba76-9ffed003c3e8"
first_move = True  # Track first move

def get_status(api_key):
    return requests.get("https://connect4.minsky.co/api/status", headers={"api-key": api_key})

def play(api_key, column):
    return requests.post("https://connect4.minsky.co/api/play", headers={"api-key": api_key, "column": str(column)})

def join_game(api_key):
    return requests.post("https://connect4.minsky.co/api/join_game", headers={"api-key": api_key})

def leave_game(api_key):
    return requests.post("https://connect4.minsky.co/api/leave_game", headers={"api-key": api_key})

def is_valid_move(board, col):
    return board[0][col] == 0

def check_victory(board, player):
    for row in range(6):
        for col in range(7):
            if col <= 3 and all(board[row][col + i] == player for i in range(4)):  # Horizontal
                return True
            if row <= 2 and all(board[row + i][col] == player for i in range(4)):  # Vertical
                return True
            if row <= 2 and col <= 3 and all(board[row + i][col + i] == player for i in range(4)):  # Diagonal /
                return True
            if row <= 2 and col >= 3 and all(board[row + i][col - i] == player for i in range(4)):  # Diagonal \
                return True
    return False

def would_win(board, col, player):
    temp_board = [row[:] for row in board]  # Copy board
    for row in reversed(range(6)):  # Start from the bottom row
        if temp_board[row][col] == 0:
            temp_board[row][col] = player  # Simulate move
            return check_victory(temp_board, player)  # Check if it wins
    return False

def bot_choice(board):
    global first_move

    for col in range(7):
        if is_valid_move(board, col) and would_win(board, col, 1):  
            return play(key, col)

    for col in range(7):
        if is_valid_move(board, col) and would_win(board, col, 2):  
            return play(key, col)

    if first_move:
        first_move = False
        options = [col for col in [2, 3, 4] if is_valid_move(board, col)]
        if options:
            return play(key, random.choice(options))

    valid_moves = [col for col in range(7) if is_valid_move(board, col)]
    if valid_moves:
        return play(key, random.choice(valid_moves))
    return None

def full_play(key):
    r = get_status(key)
    if r.status_code == 200:
        game_status = r.json()['code']
        
        if game_status == 9: 
            r = join_game(key)
            print(r.json()['text'])
        
        elif game_status == 6:
            if r.json()['your turn']:
                print("Your turn")
                bot_choice(r.json()['board'])
            else:
                print("Opponent's turn")
        elif game_status == 18: 
            print("Game ongoing")
        else: 
            print(r.json()['text'])
    else:
        print(r.content)
    
    threading.Timer(10, full_play, [key]).start()

full_play(key)
