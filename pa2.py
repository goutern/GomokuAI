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

from pa2_gomoku import Player


class AIPlayer(Player):
    """ a subclass of Player that looks ahead some number of moves and 
    strategically determines its best next move.
    """

    def __init__(self, checker):
        # This part seems useless...
        super().__init__(checker)
        self.isolated = 0
        self.game_size = 0
        self.minimizer = 0
        self.maximizer = 1
        self.depth = 3

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

        # Here I just try to find the position that has max score.
        # But I am not sure whether it is a proper way.
        # FEEL FREE TO CHANGE ANYTHING!

        if self.isolated == 0:
            self.game_size = len(board)
            self.isolated = [[False] * len(board) for i in range(board)]

        max_score = -10000  # keep the max score
        best_row, best_col = 0, 0  # keep the position of best score
        alpha = -10000
        beta = 10000

        # first step of alpha beta alg.
        for row in range(board.width):
            for col in range(board.height):
                # skip some positions(see alphabeta in detail)
                if not board.can_add_to(row, col):
                    continue
                if self.isolated[row][col]:
                    continue

                # search the tree
                board.add_checker(self.checker, row, col)
                isolate_temp = [[i for i in board[j]] for j in board]
                self.update_isolate(row, col, 2)
                score = self.alphabeta(board, self.depth, alpha, beta, False)
                board.remove_checker(self.checker, row, col)
                self.isolated = isolate_temp

                # pick the biggest score
                if score > max_score:
                    max_score = score
                    best_row, best_col = row, col
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
        if depth == 0 or self.is_win(row, col, board):
            return self.compute_score(row, col, board, maximizingPlayer)

        if maximizingPlayer:
            value = -100000
            for child_row in range(board.width):
                for child_col in range(board.height):
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
                    if self.isolated[child_row][child_col]:
                        continue

                    # search tree, backtrack
                    board.add_checker(self.checker, child_row, child_col)
                    isolate_temp = [[i for i in board[j]] for j in board]
                    self.update_isolate(child_row, child_col, 2)
                    value = max(value, self.alphabeta(board, child_row, child_col, depth - 1, alpha, beta, False))
                    self.remove_checker(child_row, child_col, board)
                    self.isolated = isolate_temp

                    # compare
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break  # (* beta cutoff *)
            return value
        else:
            value = 100000
            for child_row in range(board.width):
                for child_col in range(board.height):
                    if not board.can_add_to(child_row, child_col):
                        continue

                    if self.isolated[child_row][child_col]:
                        continue

                    board.add_checker(self.opponent_checker(), child_row, child_col)
                    isolate_temp = [[i for i in board[j]] for j in board]
                    self.update_isolate(child_row, child_col, 2)
                    value = min(value, self, self.alphabeta(board, child_row, child_col, depth - 1, alpha, beta, True))
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
                if we achieve open five and open four, we will win, so we give then extremely high scores.
                open three: attack! _XXX_
                open two: _XX_
                dead four: OXXXX_
                dead three: OXXX_
                dead two: OXX_
                single: _X_
            3. use the number of ways of winning. It may be quite good when we only have open2/dead2/dead3
        """

        return

    def remove_checker(self, row, col, board):
        """ help function
        """
        if not board.can_add_to(row, col):
            board.slots[row][col] = " "

    def update_isolate(self, row, col, layer):
        for row_index in range(max(row - layer, 0), min(row + layer + 1, self.game_size)):
            if row_index < 0 or row_index > self.game_size:
                continue
            for col_index in range(max(col - layer, 0), min(col + layer + 1, self.game_size)):
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
            board.is_win_for(self.checker, row, col)  # 5

        else:
            board.is_win_for(self.opponent_checker(), row, col)

    def check_open4(self, row, col, board):
        """
            I copy part of the codes from pa2_gomoku.py(Class Board).
            Add num_checker, then we can check different situations
        """
        if self.is_horizontal_win(self.checker, row, col, 4, board) \
                or self.is_vertical_win(self.checker, row, col, 4, board) \
                or self.is_diagonal1_win(self.checker, row, col, 4, board) \
                or self.is_diagonal2_win(self.checker, row, col, 4, board):
            return 8888
        else:
            return 0

    def check_double_open3(self, row, col, board):
        if [self.is_horizontal_win(self.checker, row, col, 3, board),
            self.is_vertical_win(self.checker, row, col, 3, board),
            self.is_diagonal1_win(self.checker, row, col, 3, board),
            self.is_diagonal2_win(self.checker, row, col, 3, board)].count(True) >= 2:
            return 7777
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

    # def meet_tree(self, board, choice):
    #
    #     # When the opponent have 3 consecutive pieces, we only have 2 choices
    #
    #     return

    # def meet_four(self, head, tail):
    #     # When the opponent has 4 consecutive pieces, we pnly have one choices
    #     return np.sign(tail[0] - head[0]) + tail[0], np.sign(tail[1] - head[1]) + tail[1]
