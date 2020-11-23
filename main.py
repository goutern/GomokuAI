from pa2_gomoku import Board, Player
import pa2
import pa22
from pa2_process import *

if __name__ == '__main__':
    # p1_s, p2_s = 0, 0
    # for i in range(0,25):
    #     print("start game", i)
    #     p1 = pa22.AIPlayer('O')
    #     p2 = pa2.AIPlayer('X')
    #     gomoku(p2, p1)
    #
    # p1_s, p2_s = 0, 0
    for i in range(0,13):
        print("start game",i+13)
        p1 = pa22.AIPlayer('X')
        p2 = pa2.AIPlayer('O')

        gomoku(p1, p2)
#### test case #####
# p1 = Player('X')
# move = p1.next_move(b1)
# print('Player ' + p1.checker + ' places a checker at position ' + str(move))
# p2 = RandomPlayer('O')
# move = p2.next_move(b1)
# print('Player ' + p2.checker + ' places a checker at position ' + str(move))
# b1.add_checker(p2.checker, move[0], move[1])
# print(b1)

####################
