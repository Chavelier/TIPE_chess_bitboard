# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 11:39:03 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

ENGINE
"""

from init import *

class Engine:
    """ classe qui gère l'ordinateur """

    def __init__(self):
        self.ply = 0 # compteur des demis coups


    def bot_move(self,depth,board):
        self.nodes = 0 # compteur des coups
        self.best_move = 0 #on initialise le meilleur coup
        score = self.alphabeta(-50000,50000,depth,board)
        # score = self.minmax(depth,board)
        return (self.best_move,score)



    def alphabeta(self,alpha,beta,depth,b):
        """ algorithme de recherche du meilleur coup """

        if depth == 0:
            return b.naive_eval()
            # return b.evaluation(False)
            # return self.quiescence(alpha, beta, b) # on fait appel à la fonction de recherche simplifiée

        in_check = b.square_is_attacked(b.ls1b_index(b.bitboard[K+6*b.side]), 1^b.side) # est ce que le roi est en echec
        self.nodes += 1
        best_sofar = 0
        old_alpha = alpha

        is_legal_move = False

        move_list = b.move_generation(b.side)
        for mv in move_list:
            if not b.make_move(mv): # le coup n'est pas legal
                continue # on le passe donc
            is_legal_move = True # il existe un coup legal

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

        if not is_legal_move:
            if in_check:
                return -49000+self.ply # si echec alors il y a mat (le + self.ply assure le mat le plus court)
            else:
                return 0 # sinon c'est pat

        if old_alpha != alpha: #on a trouvé un meilleur coup
            # coup = CASES[b.get_move_source(best_sofar)] + CASES[b.get_move_target(best_sofar)] + PIECE_LETTER[b.get_move_promotion(best_sofar)].lower()
            # print("alpha : %s"%alpha)
            # print("beta : %s"%beta)
            # print("le meilleur coup a été actualisé à %s \n"%coup)
            self.best_move = best_sofar
        return alpha



    def quiescence(self,alpha,beta,b):
        """ algorithme alpha beta simplifié pour éviter l'effet d'horizon """

        eval = b.evaluation(False)
        if eval >= beta: # le coup n'est pas optimal pour un des deux cotés
            return beta
        if eval > alpha:
            alpha = eval

        move_list = b.move_generation(b.side)
        for mv in move_list:
            if not b.make_move(mv,True): #on ne regarde que les captures
                continue # le coup n'est pas legal, on le passe donc

            self.ply += 1
            score = -self.quiescence(-beta,-alpha,b)
            self.ply -=1
            b.undo_move(True)

            if score >= beta:
                return beta
            if score > alpha: #on a trouvé un meilleur coup
                alpha = score
        return alpha
