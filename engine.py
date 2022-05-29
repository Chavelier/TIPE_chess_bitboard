# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 11:39:03 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

ENGINE
"""

from board import *

# constantes
MAX_PLY = 64 # profondeur de recherche maximum
ASPIRATION_WINDOW = 50 # utile pour la recherche en profondeur itérative
FULL_DEPTH_MOVES = 4 # le nombre de coups qu'on regarde avant de réduire potentiellement les suivants
REDUCTION_LIMIT = 3

class Engine:
    """ Représentation de l'intelligence artificielle """

    def __init__(self):
        self.ply = 0 # compteur de la profondeur (en demi coups)
        self.clear_variables()

        # hash variables
        self.piece_keys = [[0 for _ in range(64)] for _ in range(12)]
        self.enpassant_keys = [0 for _ in range(64)]
        self.castle_keys = [0 for _ in range(16)]
        self.side_key = 0
        self.init_random_keys()


    def clear_variables(self):
        self.pv_length = [0 for _ in range(MAX_PLY)]
        self.pv_table = [[Move() for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]

        self.killer_moves = [[Move() for _ in range(MAX_PLY)],[Move() for _ in range(MAX_PLY)]] # utile dans le tri des coups
        self.history_moves = [[0 for _ in range(64)] for _ in range(12)] # utile dans le tri des coups


    def bot_move(self,depth,board):

        # tri PV variables
        self.is_following_pv = False
        self.is_score_pv = False
        # statistiques sur l'ia
        self.nodes = 0 # compteur des noeuds visités
        self.max_depth = 0
        self.clear_variables()


        # recherche en profondeur itérative
        temps_tot = 0
        alpha = -50000
        beta = 50000
        print("Profondeur    Noeuds    Profondeur maximale    Temps    Principale variation\n")
        for current_depth in range(1,depth+1):
            self.is_following_pv = True
            # statistiques sur l'ia
            self.nodes = 0 # compteur des noeuds visités
            self.max_depth = 0

            tic = time.time()

            score = self.alphabeta(alpha,beta,current_depth,board)
            if score <= alpha or score >= beta:
                alpha = -50000
                beta = 50000
                print("erreur de fenêtre")
                score = self.alphabeta(alpha,beta,current_depth,board)
                # voir si on a besoin de calculer cette valeur ou si on peut continue
            else:
                alpha = score-ASPIRATION_WINDOW
                beta = score+ASPIRATION_WINDOW

            tac = time.time()
            temps = tac - tic
            temps_tot += temps

            pv = ""
            for i in range(self.pv_length[0]):
                move = self.pv_table[0][i]
                pv += move.txt(True)+" "
            ligne = " "*9+str(current_depth)
            ligne += " "*(10-len(str(self.nodes)))+str(self.nodes)
            ligne += " "*(23-len(str(self.max_depth)))+str(self.max_depth)
            ligne +=" "*(8-len(str(round(time.time()-tic,2))))+str(round(temps,2))+"s"
            ligne += " "*4+pv
            print(ligne)
        print("\nScore calculé : %s"%score)
        print("Temps total : %ss\n\n\n"%round(temps_tot,3))


        # # efficacité iteration comparaison
        # self.clear_variables()
        # # statistiques sur l'ia
        # self.nodes = 0 # compteur des noeuds visités
        # self.max_depth = 0
        # # tri PV variables
        # self.is_following_pv = False
        # self.is_score_pv = False
        #
        # tic = time.time()
        # score = self.alphabeta(-50000,50000,depth,board)
        # pv = ""
        # for i in range(self.pv_length[0]):
        #     move = self.pv_table[0][i]
        #     pv += move.txt()+" "
        # print("Principale variation : %s"%pv)
        # print("Score calculé : %s"%score)
        # print("Noeuds visités : %s"%self.nodes)
        # print("Profondeur maximale atteinte : %s"%self.max_depth)
        # print("Temps de calcul : %ss"%(time.time()-tic))

        return self.pv_table[0][0]



    def alphabeta(self,alpha,beta,depth,board):
        """ algorithme de recherche du meilleur coup """

        self.pv_length[self.ply] = self.ply # a voir si on peut pas écrire ça dans bot move

        if depth == 0:
            # return board.naive_eval()
            # return board.evaluation(False)
            return self.quiescence(alpha, beta, board) # on fait appel à la fonction de recherche simplifiée
        if self.ply >= MAX_PLY: #pour ne pas aller trop loin dans la recherche
            return board.evaluation(False)

        in_check = board.square_is_attacked(board.ls1b_index(board.bitboard[K+6*board.side]), 1^board.side) # est ce que le roi est en echec
        if in_check: # on ne cherche un peu plus loin si il y a echec
            depth += 1

        self.nodes += 1
        is_legal_move = False

        # élagage par coup nul
        # attention au zugzang ! (mais c en finale et en finale on a un autre systeme)
        if depth >= 3 and self.ply and not in_check:
            board.side ^= 1 # on change le côté qui joue (on donne littéralement un coup en plus)
            board.en_passant = -1 # on le réinitialise pour éviter des coups etranges
            board.add_to_history() # on ajoute cette étrange position à l'historique afin de pouvoir appliquer l'algorithme dessus
            score = -self.alphabeta(-beta, -beta+1, depth-3, board) # on regarde simplement si il existe un "bon coup" pour l'autre cote a une profondeur réduite
            board.undo_move(True)
            if score >= beta: # il n'en existe pas
                return beta # on suppose donc que un de nos coups va laisser cette position superieure à beta

        move_list = board.move_generation(board.side)
        if self.is_following_pv:
            self.enable_pv_scoring(move_list)
        move_list = self.tri_move(move_list,board) # on tri les coups avec la méthode MVV LVA
        # rd.shuffle(move_list) ### l'ordre a une importance

        moves_searched = 0 # nombre de coups analysés
        for mv in move_list:
            if not board.make_move(mv): # le coup n'est pas legal
                continue # on le passe donc
            is_legal_move = True # il existe un coup legal

            self.ply += 1


            #### DETERMINATION DU SCORE ####
            if moves_searched == 0: # on fait une recherche normale
                score = -self.alphabeta(-beta,-alpha,depth-1,board)
            else: # Late Move Reduction (LMR)
                if moves_searched >= FULL_DEPTH_MOVES and depth >= REDUCTION_LIMIT and not in_check and not mv.capture and mv.promotion == NO_PIECE: # condition pour considerer la LMR
                    score = -self.alphabeta(-alpha-1, -alpha, depth-2, board)
                else:
                    score = alpha + 1
                if score > alpha: # PVS
                    score = -self.alphabeta(-alpha-1,-alpha,depth-1,board) # on recherche en supposant que tous les coups restants sont moins bons
                    if score > alpha and score < beta: # on s'est trompé il existe, un meilleur coup, on a perdu du temps mais globalement c'est plus efficace
                        score = -self.alphabeta(-beta,-alpha,depth-1,board)
            #### FIN DETERMINATION DU SCORE ####


            self.ply -=1
            board.undo_move(True)
            moves_searched += 1

            if score >= beta: # fail high-> on coupe cette partie
                if not mv.capture: # on n'enregistre seulement les coups discrets
                    self.killer_moves[1][self.ply] = self.killer_moves[0][self.ply] # on garde en mémoire l'ancien killer move
                    self.killer_moves[0][self.ply] = mv # on enregistre le killer move

                return beta

            if score > alpha: #on a trouvé un meilleur coup, on est donc dans la variation principale
                if not mv.capture: # on n'enregistre seulement les coups discrets
                    self.history_moves[mv.piece][mv.target] += depth # enlève des noeuds mais pas l'impression que ça accélère

                alpha = score

                # on écrit la principale variation
                self.pv_table[self.ply][self.ply] = mv
                #on recopie dans les branches supérieures les anciens coups
                for next_ply in range(self.ply+1,self.pv_length[self.ply+1]):
                    self.pv_table[self.ply][next_ply] = self.pv_table[self.ply + 1][next_ply]
                self.pv_length[self.ply] = self.pv_length[self.ply+1]

        if not is_legal_move:
            if in_check:
                return -49000+self.ply # si echec alors il y a mat (le + self.ply assure le mat le plus court)
            else:
                return 0 # sinon c'est pat

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
        if self.ply >= MAX_PLY: #pour ne pas aller trop loin dans la recherche
            return board.evaluation(False)

        move_list = board.move_generation(board.side)
        move_list = self.tri_move(move_list,board) # on tri les coups avec la méthode MVV LVA
        for mv in move_list:
            if not board.make_move(mv,True): #on ne regarde que les captures
                continue # le coup n'est pas legal, on le passe donc
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

    """
        Les coups sont ordonnés de la manière suivante :
        1. PV moves
        2. capture MVV_LVA
        3. 1er killer move
        4. 2nd killer move
        5. history moves
        6. les autres
    """

    def score_move(self,move,board):
        """ renvoi un score a un coup pour permettre de trier l'ordre des coups pour l'algorithme alpha-beta """
        if self.is_score_pv and move.id == self.pv_table[0][self.ply].id:
            self.is_score_pv = False
            return 20000 # on met les coups de la principale variation en premier
        if not move.capture: # on attribue une valeur plus faible aux coups ne capturant rien
            if move.id == self.killer_moves[0][self.ply].id:
                return 9000
            if move.id == self.killer_moves[1][self.ply].id:
                return 8000
            return self.history_moves[move.piece][move.target]


        attaquant = move.piece
        target = move.target
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

    def enable_pv_scoring(self,move_list):
        self.is_following_pv = False

        for mv in move_list:
            if mv.id == self.pv_table[0][self.ply].id:
                self.is_score_pv = True
                self.is_following_pv = True


######################################################################################################
########### TABLE DES TRANSPOSITIONS #################################################################
######################################################################################################

    def init_random_keys(self):
        """ génère les clés pour la table de transposition """
        cle_pot = cle_pot = rd.randint(0,ALL)
        used_keys = []

        for piece in range(12):
            for case in range(64):
                while cle_pot in used_keys:
                    cle_pot = rd.randint(0,ALL)
                used_keys.append(cle_pot)
                self.piece_keys[piece][case] = cle_pot
        for case in range(64):
            while cle_pot in used_keys:
                cle_pot = rd.randint(0,ALL)
            used_keys.append(cle_pot)
            self.enpassant_keys[case] = cle_pot
        for right in range(16):
            while cle_pot in used_keys:
                cle_pot = rd.randint(0,ALL)
            used_keys.append(cle_pot)
            self.castle_keys[right] = cle_pot
        while cle_pot in used_keys:
            cle_pot = rd.randint(0,ALL)
        used_keys.append(cle_pot)
        self.side_key = cle_pot
