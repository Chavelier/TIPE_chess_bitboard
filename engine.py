# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 11:39:03 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

ENGINE
"""
MIN_INT = -10000000
MAX_INT = 10000000

class Engine:
    """ classe qui gère l'ordinateur """

    def __init__(self):
        self.ply = 0 # compteur des demis coups


    def bot_move(self,depth,board):
        self.nodes = 0 # compteur des coups
        self.best_move = 0 #on initialise le meilleur coup
        score = self.negamax(-500000,500000,depth,board)
        # score = self.minmax(depth,board)
        return (self.best_move,score)

    def negamax(self,alpha,beta,depth,board):
        """ algorithme de recherche du meilleur coup """

        if depth == 0:
            return board.evaluation()

        self.nodes += 1
        old_alpha = alpha

        move_list = board.move_generation(board.side)
        for mv in move_list:
            if not board.make_move(mv): # le coup n'est pas legal
                continue # on le passe donc
            self.ply += 1
            score = -self.negamax(-beta,-alpha,depth-1,board)
            board.undo_move(True)
            self.ply -=1


            if score >= beta:
                return beta

            if score > alpha:
                alpha = score

                if self.ply == 0 and old_alpha != alpha:
                    self.best_move = mv # on associe comme meilleur coup de départ celui qui donne le meilleur score

        return alpha




    def minmax(self,depth,b):
        # algorithme minmax sans élagage

        if depth == 0: # ou mat
            return b.evaluation(False)

        score = MIN_INT

        move_list = b.move_generation(b.side)
        for mv in move_list:
            if not b.make_move(mv): # le coup n'est pas legal
                continue # on le passe donc
            self.ply += 1
            old_score = score
            score = max(score,-self.minmax(depth-1,b))
            b.undo_move(True)
            self.ply -= 1

            if self.ply == 0 and old_score != score:
                self.best_move = mv

        return score
