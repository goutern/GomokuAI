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

import copy


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
        self.max_depth = 2
        self.my_checkers = []
        self.my_moves = []
        self.opponent_first_checkers = []
        self.opponent_factor = 0.95
        self.layer = 1
        self.max_vals = []
        self.min_vals = []
        self.checker_list = [self.opponent_checker(), self.checker]
        self.direction = [[0, 1], [1, 0], [1, 1], [1, -1]]
        self.score_dict = {
            1: 10,
            2: 100,
            3: 1000,
            4: 10000,
            5: 100000,
        }
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

        self.isolated = [[False] * board.width for i in range(board.height)]

        if self.num_moves <= 2:
            self.pinpoint_checker(board)
            first_move = self.first_moves(board.height, board.width)
            if first_move:
                self.my_moves.append(list(first_move))
                return first_move

        for row in range(board.height):
            for col in range(board.width):
                if not board.can_add_to(row, col):
                    self.update_isolate(row, col, self.layer, board.height, board.width)

        max_score = -1000000  # keep the max score
        best_row, best_col = -1, -1  # keep the position of best score
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
                isolate_temp = copy.deepcopy(self.isolated)
                self.update_isolate(row, col, self.layer, board.height, board.width)
                score = -self.compute_score(row, col, board, True, self.depth) \
                        -self.alphabeta(board, row, col, self.depth, -beta, -alpha, False)
                self.remove_checker(row, col, board)
                self.isolated = isolate_temp

                # pick the biggest score
                if score > alpha:
                    if score >= beta:
                        break
                    alpha = score
                    best_row, best_col = row, col

        print(alpha)
        # self.my_moves.append([best_row, best_col])
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

        # win_score = self.is_win(row, col, board, maximizingPlayer)
        if depth == 0 or board.is_win_for(self.checker, row, col) or \
                board.is_win_for(self.opponent_checker(), row, col):
            return self.compute_score(row, col, board, maximizingPlayer, depth)

        for child_row in range(board.height):
            for child_col in range(board.width):
                # If this position if full, skip
                if not board.can_add_to(child_row, child_col):
                    continue

                if not self.isolated[child_row][child_col]:
                    continue

                # search tree, backtrack
                board.add_checker(self.checker_list[maximizingPlayer], child_row, child_col)
                isolate_temp = copy.deepcopy(self.isolated)
                self.update_isolate(child_row, child_col, self.layer, board.height, board.width)
                score = -self.compute_score(child_row, child_col, board, maximizingPlayer, depth) \
                        -self.alphabeta(board, child_row, child_col, depth - 1, -beta, -alpha, not maximizingPlayer)
                self.remove_checker(child_row, child_col, board)

                self.isolated = isolate_temp

                # compare
                if score > alpha:
                    if score >= beta:
                        return beta
                    alpha = score
        return alpha
        # else:
        #     value = 1000000
        #     for child_row in range(board.height):
        #         for child_col in range(board.width):
        #             if not board.can_add_to(child_row, child_col):
        #                 continue
        #
        #             if not self.isolated[child_row][child_col]:
        #                 continue
        #
        #             board.add_checker(self.opponent_checker(), child_row, child_col)
        #             isolate_temp = self.isolated[:]
        #             self.update_isolate(child_row, child_col, self.layer, board.height, board.width)
        #             value = min(value, self.alphabeta(board, child_row, child_col, depth - 1,  -alpha, -beta, True))
        #             self.remove_checker(child_row, child_col, board)
        #             self.isolated = isolate_temp
        #
        #             beta = min(beta, value)
        #             if beta <= alpha:
        #                 break  # (* alpha cutoff *)
        #     return -value

    def compute_score(self, row, col, board, maximizingPlayer, depth):
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
        my_score = 0
        op_score = 0
        for direction in self.direction:
            num_checkers, is_open = self.direction_check(self.checker_list[maximizingPlayer],
                                                         row, col, board, direction[0], direction[1])
            if is_open == 2:
                my_score += self.score_dict[num_checkers]
            elif is_open == 1:
                my_score += self.score_dict[num_checkers] * 0.5

        for direction in self.direction:
            num_checkers, is_open = self.direction_check(self.checker_list[not maximizingPlayer],
                                                         row, col, board, direction[0], direction[1])
            if is_open == 2:
                op_score += self.score_dict[num_checkers]
            elif is_open == 1:
                op_score += self.score_dict[num_checkers] * 0.5

        # score = self.is_win(row, col, board, maximizingPlayer)

        # score should be my score - opponent's score... I don't know how to expalin that, but everyone use this score.
        # score += self.check_single_open5(self.checker, row, col, board)
        # score += self.check_single_open5(self.opponent_checker(), row, col, board) * 2)
        # score += self.check_single_open4(self.checker, row, col, board)
        # score += (self.check_single_open4(self.opponent_checker, row, col, board) * 2)
        # score += self.check_double_open3(self.checker, row, col, board)
        # score += (self.check_double_open3(self.opponent_checker, row, col, board) * 2)

        # score += 300 if self.myopen3 else 0
        # score += score - 300 * 10 if self.myopen3 else score

        # todo: check 2 (I want to build a function to check all the situation(open3, open2) at the same time)
        # score += self.check_single_open2(self.checker, row, col, board)
        # score += self.check_single_open2(self.opponent_checker(), row, col, board)

        return (my_score - op_score * 0.5) * depth  # I set this so I can run the game and see what our AI can do currently

    def remove_checker(self, row, col, board):
        """ help function
        """
        if not board.can_add_to(row, col):
            board.slots[row][col] = " "

    def update_isolate(self, row, col, layer, row_size, col_size):
        for row_index in range(max(row - layer, 0), min(row + layer + 1, row_size)):
            for col_index in range(max(col - layer, 0), min(col + layer + 1, col_size)):
                self.isolated[row_index][col_index] = True

    def is_win(self, row, col, board, maximizingPlayer):
        """
            After add checker to this position, we have
            5, open 4, double open 4, we will win. So this is the terminate node
        """

        my_point = self.check_5(self.checker_list[maximizingPlayer], row, col, board) or \
                   self.check_open4(self.checker_list[maximizingPlayer], row, col, board) or \
                   self.check_double_open3(self.checker_list[maximizingPlayer], row, col, board)
        opponent_point = self.check_5(self.checker_list[not maximizingPlayer], row, col, board) or \
                         self.check_open4(self.checker_list[not maximizingPlayer], row, col, board) or \
                         self.check_double_open3(self.checker_list[not maximizingPlayer], row, col, board)

        return my_point - opponent_point * 0.1

    def check_5(self, checker, row, col, board):
        if board.is_win_for(self.checker, row, col):
            return 100000
        else:
            return 0

    def check_open4(self, checker, row, col, board):

        # I use OR instead of list.count, Because Short circuit will save time
        num, is_open = self.is_horizontal_win(checker, row, col, 4, board)
        if num and is_open:
            return self.score_dict[4]
        num, is_open = self.is_vertical_win(checker, row, col, 4, board)
        if num and is_open:
            return self.score_dict[4]
        num, is_open = self.is_diagonal2_win(checker, row, col, 4, board)
        if num and is_open:
            return self.score_dict[4]
        num, is_open = self.is_diagonal1_win(checker, row, col, 4, board)
        if num and is_open:
            return self.score_dict[4]
        else:
            return 0

    def check_double_open3(self, checker, row, col, board):
        count = 0
        if self.is_horizontal_win(checker, row, col, 3, board).count(True) == 2:
            count += 1
        if self.is_vertical_win(checker, row, col, 3, board).count(True) == 2:
            count += 1
            if count == 2:
                return self.score_dict[3] * 8
        if self.is_diagonal1_win(checker, row, col, 3, board).count(True) == 2:
            count += 1
            if count == 2:
                return self.score_dict[3] * 8
        if self.is_diagonal2_win(checker, row, col, 3, board).count(True) == 2:
            count += 1
            if count == 2:
                return self.score_dict[3] * 8
        if count == 1:
            self.open3 = True
            return self.score_dict[3]
        return 0

    # def check_single_open3(self, checker, row, col, board):
    #     return [self.is_horizontal_win(checker, row, col, 3, board),
    #             self.is_vertical_win(checker, row, col, 3, board),
    #             self.is_diagonal1_win(checker, row, col, 3, board),
    #             self.is_diagonal2_win(checker, row, col, 3, board)].count(True) * 1000

    def check_single_open2(self, checker, row, col, board):
        # <<<<<<< HEAD
        count = 0
        if self.is_horizontal_win(checker, row, col, 2, board).count(True) == 2:
            count += 1
        if self.is_vertical_win(checker, row, col, 2, board).count(True) == 2:
            count += 1
        if self.is_diagonal1_win(checker, row, col, 2, board).count(True) == 2:
            count += 1
        if self.is_diagonal2_win(checker, row, col, 2, board).count(True) == 2:
            count += 1
        return count * self.score_dict[2]

    def is_horizontal_win(self, checker, r, c, num_checker, board):
        cnt = 0
        is_open = True
        lower, upper = c, c

        for i in range(num_checker):
            # Check if the next four columns in this row
            # contain the specified checker.
            upper = c + i
            if upper < board.width and board.slots[r][upper] == checker:
                cnt += 1
                # print('Hl: ' + str(cnt))
            else:
                upper -= 1
                break
        if not board.can_add_to(r, upper + 1):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                if not board.can_add_to(r, lower - 1):
                    is_open = False
                return True, is_open
        else:
            # check towards left
            for i in range(1, num_checker + 1 - cnt):
                lower = c - i
                if c - i >= 0 and board.slots[r][c - i] == checker:
                    cnt += 1
                    # print('Hr: ' + str(cnt))
                else:
                    lower = lower + 1
                    break

        if not board.can_add_to(r, lower - 1):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                return True, is_open

        return False, is_open

    def is_vertical_win(self, checker, r, c, num_checker, board):
        cnt = 0
        is_open = True
        lower, upper = r, r

        for i in range(num_checker):
            # Check if the next four columns in this row
            # contain the specified checker.
            upper = r + i
            if upper < board.height and board.slots[upper][c] == checker:
                cnt += 1
                # print('Hl: ' + str(cnt))
            else:
                upper -= 1
                break
        if not board.can_add_to(upper + 1, c):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                if not board.can_add_to(lower - 1, c):
                    is_open = False
                return True, is_open
        else:
            # check towards left
            for i in range(1, num_checker + 1 - cnt):
                lower = r - i
                if lower >= 0 and board.slots[lower][c] == checker:
                    cnt += 1
                    # print('Hr: ' + str(cnt))
                else:
                    lower = lower + 1
                    break

        if not board.can_add_to(lower - 1, c):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                return True, is_open

        return False, is_open

    def is_diagonal1_win(self, checker, r, c, num_checker, board):
        cnt = 0
        is_open = True
        l_c, l_r, u_c, u_r = c, r, c, r

        for i in range(num_checker):
            u_c, u_r = c + i, r + i
            if u_r < board.height and u_c < board.width and \
                    board.slots[u_r][u_c] == checker:
                cnt += 1
                # print('D1: L ' + str(cnt))
            else:
                u_c -= 1
                u_r -= 1
                break

        if not board.can_add_to(u_r + 1, u_c + 1):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                if not board.can_add_to(l_r - 1, l_c - 1):
                    is_open = False
                return True, is_open
        else:
            for i in range(1, num_checker + 1 - cnt):
                l_c, l_r = c - i, r - i
                if l_r >= 0 and l_c >= 0 and \
                        board.slots[l_r][l_c] == checker:
                    cnt += 1
                    # print('D1: R ' + str(cnt))
                else:
                    l_r += 1
                    l_c += 1
                    break

        if not board.can_add_to(l_r - 1, l_c - 1):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                return True, is_open

        return False, is_open

    def is_diagonal2_win(self, checker, r, c, num_checker, board):
        cnt = 0
        is_open = True
        l_c, l_r, u_c, u_r = c, r, c, r

        for i in range(num_checker):
            u_c, u_r = c + i, r - i
            if u_r >= 0 and u_c < board.width and \
                    board.slots[u_r][u_c] == checker:
                cnt += 1
                # print('D1: L ' + str(cnt))
            else:
                u_c -= 1
                u_r += 1
                break

        if not board.can_add_to(u_r - 1, u_c + 1):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                if board.can_add_to(l_r + 1, l_c - 1):
                    is_open = False
                return True, is_open
        else:
            for i in range(1, num_checker + 1 - cnt):
                l_c, l_r = c - i, r + i
                if l_r < board.height and l_c >= 0 and \
                        board.slots[l_r][l_c] == checker:
                    cnt += 1
                    # print('D1: R ' + str(cnt))
                else:
                    l_r -= 1
                    l_c += 1
                    break

        if not board.can_add_to(l_r + 1, l_c - 1):
            is_open = False

        if cnt == num_checker:
            if num_checker == 5:
                return True, True
            else:
                return True, is_open

        return False, is_open

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
                    elif abs(col_diff) == 0:
                        return self.opponent_first_checkers[0][0], self.opponent_first_checkers[0][1] + 1
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

    def direction_check(self, checker, r, c, board, r_dir, c_dir):
        cnt = 0
        counter = 5
        is_open = 2
        l_c, u_c = c, c
        l_r, u_r = r, r

        for i in range(5):
            # Check if the next four columns in this row
            # contain the specified checker.
            u_c = c + i * c_dir
            u_r = r + i * r_dir
            if 0 <= u_c < board.width and 0 <= u_r < board.width and board.slots[u_r][u_c] == checker:
                cnt += 1
                counter -= 1
                # print('Hl: ' + str(cnt))
            else:
                u_c -= 1 * c_dir
                u_r -= 1 * r_dir
                break

        if cnt == 5:
            return cnt, 2
        else:
            if not board.can_add_to(u_r + 1 * r_dir, u_c + 1 * c_dir):  # cnt + counter ==5 means no skip
                is_open -= 1
            else:
                counter -= 1
                if board.can_add_to(u_r + 2 * r_dir, u_c + 2 * c_dir):
                    counter -= 1

            # check towards left
            for i in range(1, 5 + 1 - cnt):
                l_c = c - i * c_dir
                l_r = r - i * r_dir
                if 0 <= l_c < board.width and 0 <= l_r < board.width and board.slots[l_r][l_c] == checker:
                    cnt += 1
                    counter -= 1
                    # print('Hr: ' + str(cnt))
                else:
                    l_c += 1 * c_dir
                    l_r += 1 * r_dir
                    break

            if not board.can_add_to(l_r - 1 * r_dir, l_c - 1 * c_dir):
                is_open -= 1
            else:
                counter -= 1

        if cnt == 5:
            return cnt, 2
        else:
            if not board.can_add_to(l_r - 1 * r_dir, l_c - 1 * c_dir):  # cnt + counter ==5 means no skip
                is_open -= 1
            else:
                counter -= 1
                if board.can_add_to(l_r - 2 * r_dir, l_c - 2 * c_dir):
                    counter -= 1

        if counter <= 0:
            return cnt, is_open
        else:
            return cnt, 0

    # def vertical_check(self, checker, r, c, num_checker, board):
    #     cnt = 0
    #     is_open = True
    #     lower, upper = r, r
    #
    #     for i in range(num_checker):
    #         # Check if the next four columns in this row
    #         # contain the specified checker.
    #         upper = r + i
    #         if upper < board.height and board.slots[upper][c] == checker:
    #             cnt += 1
    #             # print('Hl: ' + str(cnt))
    #         else:
    #             upper -= 1
    #             break
    #     if not board.can_add_to(upper + 1, c):
    #         is_open = False
    #
    #     if cnt == num_checker:
    #         if num_checker == 5:
    #             return True, True
    #         else:
    #             if not board.can_add_to(lower - 1, c):
    #                 is_open = False
    #             return True, is_open
    #     else:
    #         # check towards left
    #         for i in range(1, num_checker + 1 - cnt):
    #             lower = r - i
    #             if lower >= 0 and board.slots[lower][c] == checker:
    #                 cnt += 1
    #                 # print('Hr: ' + str(cnt))
    #             else:
    #                 lower = lower + 1
    #                 break
    #
    #     if not board.can_add_to(lower - 1, c):
    #         is_open = False
    #
    #     if cnt == num_checker:
    #         if num_checker == 5:
    #             return True, True
    #         else:
    #             return True, is_open
    #
    #     return False, is_open
    #
    # def diagonal1_check(self, checker, r, c, num_checker, board):
    #     cnt = 0
    #     is_open = True
    #     l_c, l_r, u_c, u_r = c, r, c, r
    #
    #     for i in range(num_checker):
    #         u_c, u_r = c + i, r + i
    #         if u_r < board.height and u_c < board.width and \
    #                 board.slots[u_r][u_c] == checker:
    #             cnt += 1
    #             # print('D1: L ' + str(cnt))
    #         else:
    #             u_c -= 1
    #             u_r -= 1
    #             break
    #
    #     if not board.can_add_to(u_r + 1, u_c + 1):
    #         is_open = False
    #
    #     if cnt == num_checker:
    #         if num_checker == 5:
    #             return True, True
    #         else:
    #             if not board.can_add_to(l_r - 1, l_c - 1):
    #                 is_open = False
    #             return True, is_open
    #     else:
    #         for i in range(1, num_checker + 1 - cnt):
    #             l_c, l_r = c - i, r - i
    #             if l_r >= 0 and l_c >= 0 and \
    #                     board.slots[l_r][l_c] == checker:
    #                 cnt += 1
    #                 # print('D1: R ' + str(cnt))
    #             else:
    #                 l_r += 1
    #                 l_c += 1
    #                 break
    #
    #     if not board.can_add_to(l_r - 1, l_c - 1):
    #         is_open = False
    #
    #     if cnt == num_checker:
    #         if num_checker == 5:
    #             return True, True
    #         else:
    #             return True, is_open
    #
    #     return False, is_open
    #
    # def diagonal2_check(self, checker, r, c, num_checker, board):
    #     cnt = 0
    #     is_open = True
    #     l_c, l_r, u_c, u_r = c, r, c, r
    #
    #     for i in range(num_checker):
    #         u_c, u_r = c + i, r - i
    #         if u_r >= 0 and u_c < board.width and \
    #                 board.slots[u_r][u_c] == checker:
    #             cnt += 1
    #             # print('D1: L ' + str(cnt))
    #         else:
    #             u_c -= 1
    #             u_r += 1
    #             break
    #
    #     if not board.can_add_to(u_r - 1, u_c + 1):
    #         is_open = False
    #
    #     if cnt == num_checker:
    #         if num_checker == 5:
    #             return True, True
    #         else:
    #             if board.can_add_to(l_r + 1, l_c - 1):
    #                 is_open = False
    #             return True, is_open
    #     else:
    #         for i in range(1, num_checker + 1 - cnt):
    #             l_c, l_r = c - i, r + i
    #             if l_r < board.height and l_c >= 0 and \
    #                     board.slots[l_r][l_c] == checker:
    #                 cnt += 1
    #                 # print('D1: R ' + str(cnt))
    #             else:
    #                 l_r -= 1
    #                 l_c += 1
    #                 break
    #
    #     if not board.can_add_to(l_r + 1, l_c - 1):
    #         is_open = False
    #
    #     if cnt == num_checker:
    #         if num_checker == 5:
    #             return True, True
    #         else:
    #             return True, is_open
    #
    #     return False, is_open
