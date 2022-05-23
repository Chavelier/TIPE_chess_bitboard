# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 11:39:03 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

ENGINE
"""
INFINITY=32000

from init import *

class Engine:
    """ classe qui gère l'ordinateur """

    def __init__(self):
        self.ply = 0 # compteur des demis coups


    def bot_move(self,depth,board):
        self.nodes = 0 # compteur des coups
        self.best_move = 0 #on initialise le meilleur coup
        score = self.alphabeta(-500000,500000,depth,board)
        # score = self.minmax(depth,board)
        return (self.best_move,score)



    def alphabeta(self,alpha,beta,depth,b):
        """ algorithme de recherche du meilleur coup """

        if depth == 0:
            return b.evaluation(False)

        self.nodes += 1
        best_sofar = 0
        old_alpha = alpha

        move_list = b.move_generation(b.side)
        for mv in move_list:
            if not b.make_move(mv): # le coup n'est pas legal
                continue # on le passe donc
            self.ply += 1
            score = -self.alphabeta(-beta,-alpha,depth-1,b)
            self.ply -=1
            b.undo_move(True)

            if score >= beta:
                return beta

            if score > alpha: #on a trouvé un meilleur coup
                alpha = score

                if self.ply == 0:
                    coup = CASES[b.get_move_source(mv)] + CASES[b.get_move_target(mv)] + PIECE_LETTER[b.get_move_promotion(mv)].lower()
                    print("meilleur coup actuellement : %s \n"%coup)
                    # self.best_move = mv
                    best_sofar = mv # on associe comme meilleur coup de départ celui qui donne le meilleur score
        
        if old_alpha != alpha: #on a trouvé un meilleur coup
            # coup = CASES[b.get_move_source(best_sofar)] + CASES[b.get_move_target(best_sofar)] + PIECE_LETTER[b.get_move_promotion(best_sofar)].lower()
            # print("alpha : %s"%alpha)
            # print("beta : %s"%beta)
            # print("le meilleur coup a été actualisé à %s \n"%coup)
            self.best_move = best_sofar
        return alpha
