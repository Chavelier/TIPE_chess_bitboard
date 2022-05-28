# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 11:39:03 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

ENGINE
"""

from board import *
import random as rd
MAX_PLY = 64 # profondeur de recherche maximum

class Engine:
    """ Représentation de l'intelligence artificielle """

    def __init__(self):
        self.ply = 0 # compteur de la profondeur (en demi coups)
        self.killer_moves = [[0 for _ in range(MAX_PLY)],[0 for _ in range(MAX_PLY)]]
        self.history_moves = [[0 for _ in range(64)] for _ in range(12)]


    def bot_move(self,depth,board):
        self.nodes = 0 # compteur des noeuds visités
        self.best_move = 0 #on initialise le meilleur coup
        self.max_depth = 0
        score = self.alphabeta(-50000,50000,depth,board)
        # score = self.minmax(depth,board)
        return (self.best_move,score,self.nodes,self.max_depth)



    def alphabeta(self,alpha,beta,depth,board):
        """ algorithme de recherche du meilleur coup """

        if depth == 0:
            # return board.naive_eval()
            # return board.evaluation(False)
            return self.quiescence(alpha, beta, board) # on fait appel à la fonction de recherche simplifiée

        in_check = board.square_is_attacked(board.ls1b_index(board.bitboard[K+6*board.side]), 1^board.side) # est ce que le roi est en echec
        if in_check: # on ne cherche un peu plus loin si il y a echec
            depth += 1

        self.nodes += 1
        best_sofar = 0
        old_alpha = alpha

        is_legal_move = False

        move_list = board.move_generation(board.side)
        move_list = self.tri_move(move_list,board) # on tri les coups avec la méthode MVV LVA
        # rd.shuffle(move_list) ### l'ordre a une importance
        for mv in move_list:
            if not board.make_move(mv): # le coup n'est pas legal
                continue # on le passe donc
            is_legal_move = True # il existe un coup legal

            self.ply += 1
            score = -self.alphabeta(-beta,-alpha,depth-1,board)
            self.ply -=1
            board.undo_move(True)

            if score >= beta: # fail hard -> on coupe cette partie
                if not board.get_move_capture(mv): # on n'enregistre seulement les coups discrets
                    self.killer_moves[1][self.ply] = self.killer_moves[0][self.ply] # on garde en mémoire l'ancien killer move
                    self.killer_moves[0][self.ply] = mv # on enregistre le killer move

                return beta

            if score > alpha: #on a trouvé un meilleur coup
                if not board.get_move_capture(mv): # on n'enregistre seulement les coups discrets
                    self.history_moves[board.get_move_piece(mv)][board.get_move_target(mv)] += depth # enlève des noeuds mais pas l'impression que ça accélère

                alpha = score

                if self.ply == 0:
                    # coup = CASES[board.get_move_source(mv)] + CASES[board.get_move_target(mv)] + PIECE_LETTER[board.get_move_promotion(mv)].lower()
                    # print("meilleur coup actuellement : %s \n"%coup)
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



    def quiescence(self,alpha,beta,board):
        """ algorithme alpha beta simplifié pour éviter l'effet d'horizon """

        self.nodes += 1

        if self.ply > self.max_depth:
            self.max_depth = self.ply

        eval = board.evaluation(False)
        if eval >= beta: # le coup n'est pas optimal pour un des deux cotés
            return beta
        if eval > alpha:
            alpha = eval
        if self.ply > MAX_PLY: #pour ne pas aller trop loin dans la recherche
            return alpha

        move_list = board.move_generation(board.side)
        move_list = self.tri_move(move_list,board) # on tri les coups avec la méthode MVV LVA
        for mv in move_list:
            if not board.make_move(mv,True): #on ne regarde que les captures
                continue # le coup n'est pas legal, on le passe donc
            # if not board.get_move_capture(mv):
            #     board.undo_move(True)
            #     continue
            self.ply += 1
            score = -self.quiescence(-beta,-alpha,board)
            self.ply -=1
            board.undo_move(True)

            if score >= beta:
                return beta
            if score > alpha: #on a trouvé un meilleur coup
                alpha = score
        return alpha


######################################################################################################
########### TRI DES COUPS ############################################################################
######################################################################################################

    def score_move(self,move,board):
        """ renvoi un score a un coup pour permettre de trier l'ordre des coups pour l'algorithme alpha-beta """

        if not board.get_move_capture(move): # on attribue une valeur plus faible aux coups ne capturant rien
            if move == self.killer_moves[0][self.ply]:
                return 9000
            if move == self.killer_moves[1][self.ply]:
                return 8000
            return self.history_moves[board.get_move_piece(move)][board.get_move_target(move)]


        attaquant = board.get_move_piece(move)
        target = board.get_move_target(move)
        offset = 6*(1^board.side)
        victime = P
        for piece in range(0+offset,6+offset):
            if board.get_bit(board.bitboard[piece],target):
                victime = piece
                break
        return 10000 + MVV_LVA[attaquant][victime]

    def tri_move(self,move_list,board):
        """ tri les coups selon leur score dans l'ordre décroissant """
        # j'utilise un tri à bulles optimisé, à voir si c mieux de faire autrement
        mv_list = move_list
        score_list = [self.score_move(mv,board) for mv in mv_list]

        def echange(i,j):
            # on échange les scores
            temp = score_list[i]
            score_list[i] = score_list[j]
            score_list[j] = temp
            # on échange les coups
            temp = mv_list[i]
            mv_list[i] = mv_list[j]
            mv_list[j] = temp

        is_echange = True
        fin = len(mv_list)-1
        while is_echange:
            is_echange = False

            for i in range(fin):
                if score_list[i] < score_list[i+1]:
                    echange(i, i+1)
                    is_echange = True
            fin -= 1
        return mv_list
