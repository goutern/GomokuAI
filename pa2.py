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
        self.savedBoard = 0  # to save the previous board, use to compare
        self.blockArea = 0  # to save the block area that we don't need to consider(seems redundant)
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

        max_score = -10000  # keep the max score
        best_row, best_col = 0, 0  # keep the position of best score
        alpha = -10000
        beta = 10000

        # first step of alpha beta alg.
        for row in range(len(board)):
            for col in range(len(board)):
                # skip some positions(see alphabeta in detail)
                if not board.can_add_to(row, col):
                    continue
                if self.is_isolated(row, col, board):
                    continue
                board.add_checker(self.checker, row, col)
                score = self.alphabeta(board, self.depth, alpha, beta, False)
                board.remove_checker(self.checker, row, col)
                if score > max_score:
                    max_score = score
                    best_row, best_col = row, col
        return best_row, best_col

    def alphabeta(self, board, depth, alpha, beta, maximizingPlayer):
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
        if depth == 0 or "node is a terminal node":
            return "the heuristic value of node"
        if maximizingPlayer:
            value = -100000
            for i in range(len(board)):
                for j in range(len(board)):
                    # If this position if full, skip
                    if not board.can_add_to(i, j):
                        continue

                    # if this position is isolated, (no other checkers nearby), we skip
                    # which position can be isolated? 2-layer or 1 layer? 2-layer means:
                    # _____
                    # _____
                    # __X__
                    # _____
                    # _____
                    # And we can keep the situation in an array like board, so we do not to compute repeatedly.
                    if self.is_isolated(i, j, board):
                        continue

                    # It is wrong here. In this way(use board as input argument),
                    # we need a function that can remove checker from the board. This should be a
                    # backtracking algorithm, we should add the check and then remove.
                    board.add_checker(self.checker, i, j)
                    value = max(value, self.alphabeta(board, depth - 1, alpha, beta, False))
                    board.remove_checker(self.checker, i, j)
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break  # (* beta cutoff *)
            return value
        else:
            value = 100000
            for i in range(len(board)):
                for j in range(len(board)):
                    if not board.can_add_to(i, j):
                        continue

                    if self.is_isolated(i, j, board):
                        continue

                    if board.can_add_to(i, j):
                        board.add_checker(self.opponent_checker(), i, j)
                        value = min(value, self, self.alphabeta(board, depth - 1, alpha, beta, True))
                        board.remove_checker(self.opponent_checker(), i, j)
                        beta = min(beta, value)
                        if beta <= alpha:
                            break  # (* alpha cutoff *)
            return value

    def is_isolated(self, row, col, borad):
        return True

    def compute_score(self, row, col, board, maximizingPlayer):
        """
            open five: "XXXXX" win! 10000 pts
            open four, double open three: "_XXXX_" or "  " gonna win! 9000 pts
            if we achieve open five and open four, we will win, so we give then extremely high scores.
            open three: attack! _XXX_
            open two: _XX_
            dead four: OXXXX_
            dead three: OXXX_
            dead two: OXX_
            single: _X_
        """

        return

    # def meet_tree(self, board, choice):
    #
    #     # When the opponent have 3 consecutive pieces, we only have 2 choices
    #
    #     return

    # def meet_four(self, head, tail):
    #     # When the opponent has 4 consecutive pieces, we pnly have one choices
    #     return np.sign(tail[0] - head[0]) + tail[0], np.sign(tail[1] - head[1]) + tail[1]
