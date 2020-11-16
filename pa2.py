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
        
        
