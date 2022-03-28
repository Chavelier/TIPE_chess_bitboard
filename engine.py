# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 11:39:03 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

ENGINE
"""


class Engine:
    """ classe qui gère l'ordinateur """

    def __init__(self):
        self.ply = 0 # compteur des demis coups


    def bot_move(self,depth,board):
        self.nodes = 0 # compteur des coups
        self.best_move = 0 #on initialise le meilleur coup
        score = self.negamax(-500000,500000,depth,board)
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

                if self.ply == 0:
                    best_sofar = mv # on associe comme meilleur coup de départ celui qui donne le meilleur score

        if old_alpha != alpha:
            self.best_move = best_sofar

        return alpha
