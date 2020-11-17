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
        self.depth = 5

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
        #
        # I have another idea that we make minimizer and maximizer to be mirror.
        # (When maximizer and minimizer face the same situation, maximizer's score is k, minimizer's score is -k)
        # then when we get the score for every position, we compare the biggest score
        # and smallest score, choose the position who has bigger abs(score).
        # (Because if minimizer has a extremely small number, and we don't block it,
        # probably the minimizer will win)

        max_score = -1 # keep the max score
        best_row, best_col = 0, 0 # keep the position of best score
        alpha = -1
        beta = 10000

        for row in range(len(board)):
            for col in range(len(board)):
                score = self.alphabeta(board, row, col, self.depth, alpha, beta, False)
                if score > max_score:
                    max_score = score
                    best_row, best_col = row, col
        return best_row, best_col

    def alphabeta(self, board, row, column, depth, alpha, beta, maximizingPlayer):
        """ return the score if we add checker to (row, column).
            row: row number of position
            col: column number of position
            depth: depth of the tree

        """
        # Need a function that calculate score based on the current board
        # Need a function to check whether it is a terminal node(game over)
        if depth == 0 or "node is a terminal node":
            return "the heuristic value of node"
        if maximizingPlayer:
            value = -100000
            for i in range(len(board)):
                for j in range(len(board)):
                    # This is the easiest way, but cost too much time. We only need to
                    # consider positions that are close to the checkers that already in the board.
                    # Then after pruning, we can go deeper.
                    if board.can_add_to(i, j):
                        # It is wrong here. In this way(use board as input argument),
                        # we need a function that can remove checker from the board. This should be a
                        # backtracking algorithm, we should add the check and then remove.
                        value = max(value, self.alphabeta(board, i, j, depth - 1, alpha, beta, False))
                        alpha = max(alpha, value)
                        if alpha >= beta:
                            break  # (* beta cutoff *)
            return value
        else:
            value = 100000
            for i in range(len(board)):
                for j in range(len(board)):
                    if board.can_add_to(i, j):
                        value = min(value, self, self.alphabeta(board, i, j, depth - 1, alpha, beta, True))
                        beta = min(beta, value)
                        if beta <= alpha:
                            break  # (* alpha cutoff *)
            return value

    # def meet_tree(self, board, choice):
    #
    #     # When the opponent have 3 consecutive pieces, we only have 2 choices
    #
    #     return

    # def meet_four(self, head, tail):
    #     # When the opponent has 4 consecutive pieces, we pnly have one choices
    #     return np.sign(tail[0] - head[0]) + tail[0], np.sign(tail[1] - head[1]) + tail[1]
