# 
# Programming Assignment 2, CS640
#
# A Gomoku (Gobang) Game
#
# Adapted from CS111
# By Yiwen Gu
#
# Playing the game 
#   

from pa2_gomoku import Board, Player
from pa2 import *


def process_move(player, board):
    """ Process the next move by the specified player using the
        specified board.
        inputs: player is an instance of the Player class or one of its
                  subclasses.
                board is a Board object.
    """
    print(str(player) + "'s turn")
 
    move = player.next_move(board)
    
    board.add_checker(player.checker, move[0], move[1])
    print()
    print(board)

    if board.is_win_for(player.checker, move[0], move[1]):
        print(player, 'wins in', player.num_moves, 'moves.')
        print('Congratulations!')
        return True
    elif board.is_full():
        print("It's a tie!")
        return True
    else:
        return False
    
def gomoku(p1, p2):
    """ Plays the Gomoku between the two specified players,
        and returns the Board object as it looks at the end of the game.
        inputs: p1 and p2 are objects representing players 
          One player should use 'X' checkers and the other should
          use 'O' checkers.
    """
    # Make sure one player is 'X' and one player is 'O'.
    if p1.checker not in 'XO' or p2.checker not in 'XO' \
       or p1.checker == p2.checker:
        print('need one X player and one O player.')
        return None

    print('Welcome to Gomoku!')
    print()
    b = Board(10,10)
    print(b)
    p1.num_moves = 0
    p2.num_moves = 0
    
    while True:
        if process_move(p1, b) == True:
            return b

        if process_move(p2, b) == True:
            return b

