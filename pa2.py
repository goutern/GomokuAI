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
        self.moves = []
        self.next = []
        self.max = 1000000
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
        self.moves = []
        max_score = -1000000  # keep the max score
        best_row, best_col = -1, -1  # keep the position of best score
        alpha = -10000000
        beta = 10000000

        # first step of alpha beta alg.
        # skip some positions(see alphabeta in detail)
        # search the tree

        score = - self.alphabeta(board, self.depth, alpha, beta, True, 0)

        # pick the biggest score
        # if score > alpha:
        #     if score > beta:
        #         return best_row, best_col
        #     alpha = score
        #     best_row, best_col = row, col

        # print(alpha)
        self.my_moves.append([best_row, best_col])
        return self.next

    def alphabeta(self, board, depth, alpha, beta, maximizingPlayer, mid_score):
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
        if len(self.moves) != 0:
            p = self.moves[-1]
            if depth == 0:
                return mid_score
            elif board.is_win_for(self.checker, p[0], p[1]) or board.is_win_for(self.opponent_checker(), p[0], p[1]):
                return self.max

        for row in range(board.height):
            for col in range(board.width):
                # If this position if full, skip
                if [row, col] in self.moves or not board.can_add_to(row, col):
                    continue

                if not self.isolated[row][col]:
                    continue

                # search tree, backtrack
                # board.add_checker(self.checker_list[maximizingPlayer], row, col)
                isolate_temp = copy.deepcopy(self.isolated)
                self.update_isolate(row, col, self.layer, board.height, board.width)
                self.moves.append([row, col])
                board.add_checker(self.checker_list[maximizingPlayer], row, col)
                if maximizingPlayer:
                    help_score = self.compute_score(row, col, board, maximizingPlayer, depth)
                else:
                    help_score = - self.compute_score(row, col, board, maximizingPlayer, depth)
                if depth == self.depth and help_score >= self.score_dict[5]:
                    self.remove_checker(row, col, board)
                    self.next = self.moves[0]
                    node = self.moves.pop()
                    return help_score
                score = - self.alphabeta(board, depth - 1, -beta, -alpha, not maximizingPlayer,
                                         help_score + mid_score * 1.2)
                self.remove_checker(row, col, board)
                node = self.moves.pop()
                # self.remove_checker(row, col, board)
                # self.moves.pop()
                self.isolated = isolate_temp

                # compare
                if score > alpha:
                    if depth == self.depth:
                        self.next = self.moves[0] if len(self.moves) > 0 else node
                    if score > beta:
                        return beta
                    alpha = score
        return alpha

    def eval(self, board, depth):
        i = 1
        score = 0
        for node in self.moves:
            if i:
                board.add_checker(self.checker_list[i], node[0], node[1])
                score += self.compute_score(node[0], node[1], board, i, depth)
                i = 0
            else:
                board.add_checker(self.checker_list[i], node[0], node[1])
                score -= self.compute_score(node[0], node[1], board, i, depth)
                i = 1
        a = 0
        for node in self.moves:
            board.slots[node[0]][node[1]] = " "
        return score

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
        has_to_block = []
        for direction in self.direction:
            num_checkers, is_open = self.direction_check(self.checker_list[maximizingPlayer],
                                                         row, col, board, direction[0], direction[1])
            if is_open == 2:
                if num_checkers >= 3:
                    has_to_block.append(num_checkers)
                    if len(has_to_block) > 1:
                        my_score += self.score_dict[num_checkers] * 3
                    else:
                        my_score += self.score_dict[num_checkers]
                else:
                    my_score += self.score_dict[num_checkers]
            elif is_open == 1:
                if num_checkers >= 4:
                    has_to_block.append(num_checkers)
                    if len(has_to_block) > 1:
                        my_score += self.score_dict[num_checkers] * 3
                    else:
                        my_score += self.score_dict[num_checkers] * 0.2
                else:
                    my_score += self.score_dict[num_checkers] * 0.2

        return my_score  # + op_score * 0.5) * depth  # I set this so I can run the game and see what our AI can do currently

    def remove_checker(self, row, col, board):
        """ help function
        """
        if not board.can_add_to(row, col):
            board.slots[row][col] = " "

    def update_isolate(self, row, col, layer, row_size, col_size):
        for row_index in range(max(row - layer, 0), min(row + layer + 1, row_size)):
            for col_index in range(max(col - layer, 0), min(col + layer + 1, col_size)):
                self.isolated[row_index][col_index] = True

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
            if 0 <= u_r + 1 * r_dir < board.width and 0 <= u_c + 1 * c_dir < board.height and \
                    (board.slots[u_r + 1 * r_dir][u_c + 1 * c_dir] != checker and
                     board.slots[u_r + 1 * r_dir][u_c + 1 * c_dir] != " "):  # cnt + counter ==5 means no skip
                is_open -= 1
            else:
                counter -= 1
                k = 2
                while counter > 0:
                    if 0 <= u_r + k * r_dir < board.width and 0 <= u_c + k * c_dir < board.height and \
                            (board.slots[u_r + k * r_dir][u_c + k * c_dir] == checker or
                             board.slots[u_r + k * r_dir][u_c + k * c_dir] == " "):
                        counter -= 1
                        k += 1
                    else:
                        break

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

        if cnt == 5:
            return cnt, 2
        else:
            if 0 <= l_r - 2 * r_dir < board.width and 0 <= l_c - 2 * c_dir < board.height and \
                    board.slots[l_r - 1 * r_dir][l_c - 1 * c_dir] != checker and \
                    board.slots[l_r - 1 * r_dir][l_c - 1 * c_dir] != " ":  # cnt + counter ==5 means no skip
                is_open -= 1
            else:
                counter -= 1
                k = 2
                while counter > 0:
                    if 0 <= l_r - k * r_dir < board.width and 0 <= l_c - k * c_dir < board.height and \
                            (board.slots[l_r - k * r_dir][l_c - k * c_dir] == checker or
                             board.slots[l_r - k * r_dir][l_c - k * c_dir] == " "):
                        counter -= 1
                        k += 1
                    else:
                        break

        if counter <= 0:
            return cnt, is_open
        else:
            return cnt, 0
