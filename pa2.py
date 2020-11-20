# 
# Programming Assignment 2, CS640
#
# A Gomoku (Gobang) Game
#
# Adapted from CS111
# By Yiwen Gu
#
# You need to implement an AI Player for Gomoku
# A Random Player is provided for you
# 
#
import sys

from pa2_gomoku import Player
import random
import numpy as np


class AIPlayer(Player):
    """ a subclass of Player that looks ahead some number of moves and 
    strategically determines its best next move.
    """

    def __init__(self, checker):
        # This part seems useless...
        super().__init__(checker)
        self.isolated = 0
        self.minimizer = 0
        self.maximizer = 1
        self.depth = 2
        self.my_checkers = []
        self.my_moves = []
        self.opponent_first_checkers = []
        # self.start_type  = -1

    def next_move(self, board):
        """ returns the called AIPlayer's next move for a game on
            the specified Board object. 
            input: board is a Board object for the game that the called
                     Player is playing.
            return: row, col are the coordinated of a vacant location on the board 
        """
        self.num_moves += 1

        ################### TODO: ######################################
        # Implement your strategy here. 
        # Feel free to call as many as helper functions as you want.
        # We only cares the return of this function
        ################################################################

        # 11.19 first 3 moves. It's a bit difficult to do 5 moves.

        # Here I just try to find the position that has max score.
        # But I am not sure whether it is a proper way.
        # FEEL FREE TO CHANGE ANYTHING!

        if self.isolated == 0:
            self.isolated = [[False] * board.width for i in range(board.height)]

        if self.num_moves <= 2:
            self.pinpoint_checker(board)
            first_move = self.first_moves(board.height, board.width)
            self.my_moves.append(list(first_move))
            return first_move

        for row in range(board.height):
            for col in range(board.width):
                if not board.can_add_to(row, col):
                    self.update_isolate(row, col, 2, board.height, board.width)

        max_score = -1000000  # keep the max score
        best_row, best_col = 0, 0  # keep the position of best score
        alpha = -1000000
        beta = 1000000

        # first step of alpha beta alg.
        for row in range(board.height):
            for col in range(board.width):
                # skip some positions(see alphabeta in detail)
                if not board.can_add_to(row, col):
                    continue
                if not self.isolated[row][col]:
                    continue


                # search the tree
                board.add_checker(self.checker, row, col)
                isolate_temp = self.isolated[:]
                self.update_isolate(row, col, 2, board.height, board.width)
                score = self.alphabeta(board, row, col, self.depth, alpha, beta, False)
                self.remove_checker(row, col, board)
                self.isolated = isolate_temp

                # pick the biggest score
                if score > max_score:
                    max_score = score
                    best_row, best_col = row, col
                alpha = max(alpha, score)
                if alpha >= beta:
                    break  # (* beta cutoff *)
        print(score)
        self.my_moves.append([best_row, best_col])
        return best_row, best_col

    def alphabeta(self, board, row, col, depth, alpha, beta, maximizingPlayer):
        """ return the score if we add checker to (row, column).
            row: row number of position
            col: column number of position
            depth: depth of the tree

        """
        # Need a function that calculate score based on the current board
        # Need a function to check whether it is a terminal node(game over)
        # We can use the same function to calculate both minimizer and maximizer,
        # and we need to use g = f(minimizer) + f(maximizer). consider weights? a * f(max) + b * f(min)
        # If it is maximizer's turn, score should be g. Else,  -g
        win_score = self.is_win(row, col, board, maximizingPlayer)
        if win_score:
            return 150000
        if depth == 0:
            return self.compute_score(row, col, board, maximizingPlayer)

        if maximizingPlayer:
            value = -1000000
            for child_row in range(board.height):
                for child_col in range(board.width):
                    # If this position if full, skip
                    if not board.can_add_to(child_row, child_col):
                        continue

                    # if this position is isolated, (no other checkers nearby), we skip
                    # which position can be isolated? 2-layer or 1 layer? 2-layer means:
                    # _____
                    # _____
                    # __X__
                    # _____
                    # _____
                    # And we can keep the situation in an array like board, so we do not to compute repeatedly.
                    if not self.isolated[child_row][child_col]:
                        continue

                    # search tree, backtrack
                    board.add_checker(self.checker, child_row, child_col)
                    isolate_temp = self.isolated[:]
                    self.update_isolate(child_row, child_col, 2, board.height, board.width)
                    value = max(value, self.alphabeta(board, child_row, child_col, depth - 1, alpha, beta, False))
                    self.remove_checker(child_row, child_col, board)
                    self.isolated = isolate_temp

                    # compare
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break  # (* beta cutoff *)
            return value
        else:
            value = 1000000
            for child_row in range(board.height):
                for child_col in range(board.width):
                    if not board.can_add_to(child_row, child_col):
                        continue

                    if not self.isolated[child_row][child_col]:
                        continue

                    board.add_checker(self.opponent_checker(), child_row, child_col)
                    isolate_temp = self.isolated[:]
                    self.update_isolate(child_row, child_col, 2, board.height, board.width)
                    value = min(value, self.alphabeta(board, child_row, child_col, depth - 1, alpha, beta, True))
                    self.remove_checker(child_row, child_col, board)
                    self.isolated = isolate_temp

                    beta = min(beta, value)
                    if beta <= alpha:
                        break  # (* alpha cutoff *)
            return value

    def compute_score(self, row, col, board, maximizingPlayer):
        """
            1. good start
            2. score for each situations
                open five: "XXXXX" win! 10000 pts
                open four, double open three: "_XXXX_" or "  " gonna win! 9000 pts


                open three: attack! _XXX_
                open two: _XX_
                dead four: OXXXX_
                dead three: OXXX_
                dead two: OXX_
                single: _X_
            3. use the number of ways of winning. It may be quite good when we only have open2/dead2/dead3
        """


        checker = self.checker if maximizingPlayer else self.opponent_checker()
        score = 0
        score += self.check_single_open5(self.checker, row, col, board)
        score += (self.check_single_open5(self.opponent_checker(), row, col, board) + 1000)
        score += self.check_single_open4(self.checker, row, col, board)
        score += (self.check_single_open4(self.opponent_checker, row, col, board) + 1000)
        score += self.check_double_open3(self.checker, row, col, board)
        score += (self.check_double_open3(self.opponent_checker, row, col, board) + 1000)
        score += self.check_single_open3(self.checker, row, col, board)
        score += self.check_single_open2(self.checker, row, col, board)
        # scoreAdjust = 200
        # # if not maximizingPlayer:
        # #     scoreAdjust = -scoreAdjust
        # if board.slots[min_row][min_col] == self.checker:
        #     if min_row != row and min_col != col:
        #         score += scoreAdjust
        # if board.slots[min_row][col] == self.checker:
        #     if min_row != row:
        #         score += scoreAdjust
        # if board.slots[min_row][max_col] == self.checker:
        #     if min_row != row and max_col != col:
        #         score += scoreAdjust
        # if board.slots[row][min_col] == self.checker:
        #     if min_col != col:
        #         score += scoreAdjust
        # if board.slots[row][max_col] == self.checker:
        #     if max_col != col:
        #         score += scoreAdjust
        # if board.slots[max_row][min_col] == self.checker:
        #     if max_row != row and min_col != col:
        #         score += scoreAdjust
        # if board.slots[max_row][col] == self.checker:
        #     if max_row != row:
        #         score += scoreAdjust
        # if board.slots[max_row][max_col] == self.checker:
        #     if max_row != row and max_col != col:
        #         score += scoreAdjust

        return score  # I set this so I can run the game and see what our AI can do currently

    def remove_checker(self, row, col, board):
        """ help function
        """
        if not board.can_add_to(row, col):
            board.slots[row][col] = " "

    def update_isolate(self, row, col, layer, row_size, col_size):
        for row_index in range(max(row - layer, 0), min(row + layer + 1, row_size)):
            for col_index in range(max(col - layer, 0), min(col + layer + 1, col_size)):
                self.isolated[row_index][col_index] = True
        # else:
        #     for row_index in range(max(row - layer, 0), min(row + layer + 1, self.game_size)):
        #         if row_index < 0 or row_index > self.game_size:
        #             continue
        #         for col_index in range(max(col - layer, 0), min(col + layer + 1, self.game_size)):
        #             back_to_prev(row_index,col_index,board)
        #
        # def back_to_prev(row, col):
        #     for row_index_inner in range(max(row - layer, 0), min(row + layer + 1, self.game_size)):
        #         if row_index_inner < 0 or row_index_inner > self.game_size:
        #             continue
        #         for col_index_inner in range(max(col - layer, 0), min(col + layer + 1, self.game_size)):
        #             self.isolated[row_index_inner][col_index_inner] = True

    def is_win(self, row, col, board, maximizingPlayer):
        """
            After add checker to this position, we have
            5, open 4, double open 4, we will win. So this is the terminate node
        """
        if maximizingPlayer:
            return board.is_win_for(self.checker, row, col) or \
                   self.check_double_open3(self.checker, row, col, board) or \
                   self.check_open4(self.checker, row, col, board)

        else:
            return board.is_win_for(self.opponent_checker(), row, col) or \
                   self.check_open4(self.opponent_checker(), row, col, board) or \
                   self.check_double_open3(self.opponent_checker(), row, col, board)

    def check_open4(self, checker, row, col, board):
        """
            I copy part of the codes from pa2_gomoku.py(Class Board).
            Add num_checker, then we can check different situations
        """
        if self.is_horizontal_win(checker, row, col, 4, board) \
                or self.is_vertical_win(checker, row, col, 4, board) \
                or self.is_diagonal1_win(checker, row, col, 4, board) \
                or self.is_diagonal2_win(checker, row, col, 4, board):
            return 4001
        else:
            return 0

    def check_single_open5(self, checker, row, col, board):
        if [self.is_horizontal_win(checker, row, col, 5, board),
            self.is_vertical_win(checker, row, col, 5, board),
            self.is_diagonal1_win(checker, row, col, 5, board),
            self.is_diagonal2_win(checker, row, col, 5, board)].count(True) == 1:
            return 7100
        else:
            return 0
    def check_single_open4(self, checker, row, col, board):
        if [self.is_horizontal_win(checker, row, col, 4, board),
            self.is_vertical_win(checker, row, col, 4, board),
            self.is_diagonal1_win(checker, row, col, 4, board),
            self.is_diagonal2_win(checker, row, col, 4, board)].count(True) == 1:
            return 6100
        else:
            return 0

    def check_double_open3(self, checker, row, col, board):
        if [self.is_horizontal_win(checker, row, col, 3, board),
            self.is_vertical_win(checker, row, col, 3, board),
            self.is_diagonal1_win(checker, row, col, 3, board),
            self.is_diagonal2_win(checker, row, col, 3, board)].count(True) >= 2:
            return 3010
        else:
            return 0


    def check_single_open3(self, checker, row, col, board):
        if [self.is_horizontal_win(checker, row, col, 3, board),
            self.is_vertical_win(checker, row, col, 3, board),
            self.is_diagonal1_win(checker, row, col, 3, board),
            self.is_diagonal2_win(checker, row, col, 3, board)].count(True) == 1:
            return 2100
        else:
            return 0

    def check_single_open2(self, checker, row, col, board):
        if [self.is_horizontal_win(checker, row, col, 2, board),
            self.is_vertical_win(checker, row, col, 2, board),
            self.is_diagonal1_win(checker, row, col, 2, board),
            self.is_diagonal2_win(checker, row, col, 2, board)].count(True) == 1:
            return 1555
        else:
            return 0

    def is_horizontal_win(self, checker, r, c, num_checker, board):
        cnt = 0

        for i in range(num_checker):
            # Check if the next four columns in this row
            # contain the specified checker.
            if c + i < board.width and board.slots[r][c + i] == checker:
                cnt += 1
                # print('Hl: ' + str(cnt))
            else:
                break

        if cnt == num_checker:
            return True
        else:
            # check towards left
            for i in range(1, num_checker + 1 - cnt):
                if c - i >= 0 and board.slots[r][c - i] == checker:
                    cnt += 1
                    # print('Hr: ' + str(cnt))
                else:
                    break

            if cnt == num_checker:
                return True

        return False

    def is_vertical_win(self, checker, r, c, num_checker, board):
        cnt = 0
        for i in range(num_checker):
            # Check if the next four rows in this col
            # contain the specified checker.
            if r + i < board.width and board.slots[r + i][c] == checker:
                cnt += 1
                # print('Vdwn: ' + str(cnt))
            else:
                break

        if cnt == num_checker:
            return True
        else:
            # check upwards
            for i in range(1, num_checker + 1 - cnt):
                if r - i >= 0 and board.slots[r - i][c] == checker:
                    cnt += 1
                    # print('Vup: ' + str(cnt))
                else:
                    break

            if cnt == num_checker:
                return True

        return False

    def is_diagonal1_win(self, checker, r, c, num_checker, board):
        cnt = 0
        for i in range(num_checker):
            if r + i < board.height and c + i < board.width and \
                    board.slots[r + i][c + i] == checker:
                cnt += 1
                # print('D1: L ' + str(cnt))
            else:
                break
        if cnt == num_checker:
            return True
        else:
            for i in range(1, num_checker + 1 - cnt):
                if r - i >= 0 and c - i >= 0 and \
                        board.slots[r - i][c - i] == checker:
                    cnt += 1
                    # print('D1: R ' + str(cnt))
                else:
                    break

            if cnt == num_checker:
                return True

        return False

    def is_diagonal2_win(self, checker, r, c, num_checker, board):
        cnt = 0
        for i in range(num_checker):
            if r - i >= 0 and c + i < board.width and \
                    board.slots[r - i][c + i] == checker:
                cnt += 1
                # print('D2: L ' + str(cnt))
            else:
                break

        if cnt == num_checker:
            return True
        else:
            for i in range(1, num_checker + 1 - cnt):
                if r + i < board.height and c - i >= 0 and \
                        board.slots[r + i][c - i] == checker:
                    cnt += 1
                    # print('D2: R ' + str(cnt))
                else:
                    break

            if cnt == num_checker:
                return True

        return False

    def pinpoint_checker(self, board):
        """
            only for first several moves
        """
        for row in range(board.height):
            for col in range(board.width):
                if board.slots[row][col] == " ":
                    continue
                elif board.slots[row][col] == self.checker:
                    self.my_checkers.append([row, col])
                else:
                    self.opponent_first_checkers.append([row, col])

    def first_moves(self, height, width):
        if len(self.my_checkers) == len(self.opponent_first_checkers):  # we go first
            if len(self.my_checkers) == 0:
                return height // 2, width // 2
            elif len(self.my_checkers) == 1:
                row_diff = self.my_checkers[0][0] - self.opponent_first_checkers[0][0]
                col_diff = self.my_checkers[0][1] - self.opponent_first_checkers[0][1]
                if abs(row_diff) == 1:
                    if abs(col_diff) == 1:
                        # self.start_type = "pu"
                        return 2 * self.opponent_first_checkers[0][0] - self.my_checkers[0][0], \
                               self.my_checkers[0][1]
                    else:
                        return self.my_checkers[0][0] - np.sign(col_diff), self.my_checkers[0][0] + np.sign(row_diff)
                if row_diff == 0:
                    if abs(col_diff) == 1:
                        # self.start_type = "hua"
                        return self.opponent_first_checkers[0][0] + 1, self.opponent_first_checkers[0][1]
                    else:
                        return self.my_checkers[0][0] - np.sign(col_diff), self.my_checkers[0][0] + np.sign(row_diff)
                else:
                    return self.my_checkers[0][0] - np.sign(col_diff), self.my_checkers[0][0] + np.sign(row_diff)
        else:  # go second
            if len(self.my_checkers) == 0:
                return self.opponent_first_checkers[0][0] + random.choice([1, -1]), \
                       self.opponent_first_checkers[0][1] + random.choice([1, -1])
