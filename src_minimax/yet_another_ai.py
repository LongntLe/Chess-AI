from sqlalchemy.orm import sessionmaker
from tabledef import *
import chess
import random
import hashlib

"""
Implementation of a chess engine with the Minimax algorithm and Alpha-beta Pruning.
Features:
    Real games vs the AI
    Display of the bitboard after every turn
    Minmax algorithm with the AI always playing as the maximizer
    Database to store past moves and their evaluations using a hash table
    Holistic evaluation functions: pieces values, number of pieces advantage, piece position, check/checkmate condition.
Requirements:
    python-chess
    sqlalchemy
"""

# create a database to store moves and their respective evaluation.
engine = create_engine('sqlite:///chess_db.db')

# initialize constant that would be used in various evaluation steps.
INF = 100000

# value matrices by positions. E.g. P is the matrix of values by position for white pawns, Pb is for black pawns.
# Value matrices for white and black are mirrored
# Matrices are 1D by design for ease of implementation.
# Sources: https://chessprogramming.wikispaces.com/Simplified+evaluation+function
P = [0,0,0,0,0,0,0,0,
    50,50,50,50,50,50,50,50,
    10,10,20,30,30,20,10,10,
    5,5,10,25,25,10,5,5,
    0,0,0,20,20,0,0,0,
    5,-5,-10,0,0,-10,-5,5,
    5,10,10,-20,-20,10,10,5,
    0,0,0,0,0,0,0,0]

Pb = [0,0,0,0,0,0,0,0,
    5,10,10,-20,-20,10,10,5,
    5,-5,-10,0,0,-10,-5,5,
    0,0,0,20,20,0,0,0,
    5,5,10,25,25,10,5,5,
    10,10,20,30,30,20,10,10,
    50,50,50,50,50,50,50,50,
    0,0,0,0,0,0,0,0]

N = [-50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,0,0,0,0,-20,-40,
    -30,0,10,15,15,10,0,-30,
    -30,5,15,20,20,15,5,-30,
    -30,0,15,20,20,15,0,-30,
    -30,5,10,15,15,10,5,-30,
    -40,-20,0,5,5,0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50]

Nb = [-50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,0,5,5,0,-20,-40,
    -30,5,10,15,15,10,5,-30,
    -30,0,15,20,20,15,0,-30,
    -30,5,15,20,20,15,5,-30,
    -30,0,10,15,15,10,0,-30,
    -40,-20,0,0,0,0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,]

B = [-20,-10,-10,-10,-10,-10,-10,-20,
    -10,0,0,0,0,0,0,-10,
    -10,0,5,10,10,5,0,-10,
    -10,5,5,10,10,5,5,-10,
    -10,0,10,10,10,10,0,-10,
    -10,10,10,10,10,10,10,-10,
    -10,5,0,0,0,0,5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20]

Bb = [-20,-10,-10,-10,-10,-10,-10,-20,
    -10,5,0,0,0,0,5,-10,
    -10,10,10,10,10,10,10,-10,
    -10,0,10,10,10,10,0,-10,
    -10,5,5,10,10,5,5,-10,
    -10,0,5,10,10,5,0,-10,
    -10,0,0,0,0,0,0,-10,
    -20,-10,-10,-10,-10,-10,-10,-20]

R = [0,0,0,0,0,0,0,0,
    5,10,10,10,10,10,10,5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    0,0,0,5,5,0,0,0]

Rb = [0,0,0,5,5,0,0,0,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5,
    5,10,10,10,10,10,10,5,
    0,0,0,0,0,0,0,0]

Q = [-20,-10,-10,-5,-5,-10,-10,-20,
    -10,0,0,0,0,0,0,-10,
    -10,0,5,5,5,5,0,-10,
    -5,0,5,5,5,5,0,-5,
    0,0,5,5,5,5,0,-5,
    -10,5,5,5,5,5,0,-10,
    -10,0,5,0,0,0,0,-10,
    -20,-10,-10,-5,-5,-10,-10,-20]

Qb = [-20,-10,-10,-5,-5,-10,-10,-20,
    -10,0,5,0,0,0,0,-10,
    -10,5,5,5,5,5,0,-10,
    0,0,5,5,5,5,0,-5,
    -5,0,5,5,5,5,0,-5,
    -10,0,5,5,5,5,0,-10,
    -10,0,0,0,0,0,0,-10,
    -20,-10,-10,-5,-5,-10,-10,-20]

K = [-30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20]

Kb = [20, 30, 10,  0,  0, 10, 30, 20,
    20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30]

# Implementation of Minimax, including the minimax root, min value, max value and evaluation function based on Norvig/Russell pseudo-codes, 
# with slight modifications for ease of implementation 
def minimaxRoot(depth, board, isMaximizer, white):
    """
    The base of minimax functions.
    Inputs:
        depth: the depth of the search tree
        board: the current state of the game
        isMaximizer: True if max player, False if min player
        white: whether the current player is white or black. True if white, False if black
    Outputs: The optimal move the algorithm could find in the search tree, by definition the move with the optimal value x turns ahead.
    """
    moves = board.legal_moves
    best_val = -INF
    bestMoveFinal = None
    for x in moves:
        move = chess.Move.from_uci(str(x))
        board.push(move)
        value = max(best_val, minimax(depth - 1, board,-INF,INF, not isMaximizer, white))
        board.pop()
        if (value > best_val):
            print("Best score: " ,str(best_val))
            print("Best move: ", str(bestMoveFinal))
            best_val = value
            bestMoveFinal = move
    return bestMoveFinal

def minimax(depth, board, alpha, beta, is_maximizer, white):
    """
    Implementation of the minimax algorithm as a recursion function.
    Inputs:
        depth: the depth of the search tree
        board: the current state of the board
        alpha, beta: parameters for alpha-beta pruning.
        is_maximizer: whether the turn is of the max player or the min player
        white: whether the current player is white or black
    Outputs: the optimal move for the current state of the board.
    Separated from the function above as MinimaxRoot loops through all states to find the optimal move.
    """
    if(depth == 0):
        if white:
            return evaluation(board, white)
        else:
            return -evaluation(board, white)
    moves = board.legal_moves
    if(is_maximizer):
        bestMove = -INF
        for x in moves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            bestMove = max(bestMove,minimax(depth - 1, board,alpha,beta, not is_maximizer, white))
            board.pop()
            alpha = max(alpha,bestMove)
            if beta <= alpha:
                return bestMove
        return bestMove
    else:
        bestMove = INF
        for x in moves:
            move = chess.Move.from_uci(str(x))
            board.push(move)
            bestMove = min(bestMove, minimax(depth - 1, board,alpha,beta, not is_maximizer, white))
            board.pop()
            beta = min(beta,bestMove)
            if(beta <= alpha):
                return bestMove
        return bestMove

def evaluation(board, white):
    """
    Evaluation functions. Including 3 heuristics: difference in piece value, difference in piece positions, and check/checkmate evaluation.
    The algorithm first search if a move is in the database. If yes, retrieve the move's value. If no, evaluate the position and insert the data into the database.
    """
    i = 0
    evaluation = 0
    x = True
    h = hashlib.sha256()
    h.update(str(board).encode('utf-8'))

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(Moves).filter(Moves.state==h.hexdigest())
    result = query.first()

    if result:
        return result.value
    else:
        for i in range(64):
            try:
                x = bool(board.piece_at(i).color)
            except AttributeError as e:
                x = x
            evaluation += (getPieceValue(str(board.piece_at(i)),i) if x else -getPieceValue(str(board.piece_at(i)),i))
    
        if board.is_check():
            if white == board.turn:
                evaluation -= 400
            else:
                evaluation += 400 # arbitrary value
        if board.is_checkmate():
            if white == board.turn:
                evaluation -= 10000
            else:
                evaluation += 10000
        new_move = Moves(h.hexdigest(), evaluation)
        s.add(new_move)
        s.commit()
        return evaluation


def getPieceValue(piece, i):
    """
    Helper function: evaluate the value of a piece by its rank and its current position on the board.
    Input:  
        piece: name of a piece
        i: position of the piece. (board in python-chess is an 1D array)
    Output: evaluation as a float value.
    """
    if piece == "P":
        return 100 + P[::-1][i]
    if piece == "p":
        return 100 + Pb[::-1][i]
    if piece == "N":
        return 320 + N[::-1][i]
    if piece == "n":
        return 320 + Nb[::-1][i]
    if piece == "B":
        return 330 + B[::-1][i]
    if piece == "b":
        return 330 + Bb[::-1][i]
    if piece == "R":
        return 500 + R[::-1][i]
    if piece == "r":
        return 500 + Rb[::-1][i]
    if piece == "Q":
        return 900 + Q[::-1][i]
    if piece == "q":
        return 900 + Qb[::-1][i]
    if piece == "K":
        return 10000 + K[::-1][i]
    if piece == "k":
        return 10000 + Kb[::-1][i]
    else:
        return 0

def user_move(board):
    """
    Helper function: Prompt for user's move. Only return if the move is valid
    (that is, move is legal and contains no typos.)
    Input: board state
    Output: user's move
    """
    while True:
        move = input("Enter your move: ")
        try:
            if board.parse_san(move) in board.legal_moves:
                return move

        except:
            print ("Illegal move. Please try again.")

def ai_move(board, white):
    """
    Helper function: Initialize the minimax algorithm to and return AI's move
    """
    min_move = minimaxRoot(3,board,True,white)
    return min_move

def game():
    """
    Main game engine. Initialize board, determine whether the human or the AI start first, and check for terminating conditions (checkmate/ stalemate/ etc...)
    """
    board = chess.Board() # initialize board

    if random.choice([0,1]): # determine whose turn is whose
        turn_dict = {'white':'user', 'black':'bot'}
    else:
        turn_dict = {'white':'bot', 'black':'user'}

    white = True # keep track of the current player

    while True:
        print(board) # display board

        if white: # get move either from AI or human
            if turn_dict['white'] == 'user':
                move = user_move(board)
            else:
                move = ai_move(board, white)

        else:
            if turn_dict['black'] == 'user':
                move = user_move(board)
            else:
                move = ai_move(board, white)

        try: # push the move
            board.push_san(move)
        except:
            board.push(move)

        if board.is_checkmate(): # check if game ends. Currently only limited to checkmate or tie game, but could potentially include more info.
            print(board)
            print ("White wins!") if white else print("Black wins!")
            break

        elif board.is_game_over():
            print(board)
            print("Tie game")
            break    
    
        white = not white

if __name__ == "__main__":
    game() # run game
