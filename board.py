# -*- coding: utf-8 -*-
"""
Created on Mon Feb  21 12:35:18 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

BOARD
"""

from init import *
import time

class Move:
    """ Représentation des coups """

    def __init__(self,source=0,target=0,piece=NO_PIECE,promotion=NO_PIECE,capture=0,double=0,enpassant=0,castling=0):
        self.source = source
        self.target = target
        self.piece = piece
        self.promotion = promotion
        self.capture = capture
        self.double = double
        self.enpassant = enpassant
        self.castling = castling
        self.id = self.source | (self.target << 6) | (self.piece << 12) | (self.promotion << 16) | (self.capture << 20) | (self.double << 21) | (self.enpassant << 22) | (self.castling << 23)

    def txt(self,f=True):
        mv = ""
        if f:
            mv += PIECE_LETTER[self.piece]+"_"
        mv += CASES[self.source]+CASES[self.target]+PIECE_LETTER[self.promotion].lower()
        return mv


class Board:
    """ Représentation de l'échéquier """


    def __init__(self):
        """ initialise l'échéquier """

        self.side = WHITE

        self.bitboard = [ # P N B R Q K p n b r q k
            71776119061217280,
            2**57+2**62,
            2**58+2**61,
            2**56+2**63,
            2**59,
            2**60,
            65280,
            2**1+2**6,
            2**2+2**5,
            2**0+2**7,
            2**3,
            2**4
            ]
        self.occupancies = [0,0,0]
        for i in range(6):
            self.occupancies[0] |= self.bitboard[i]
            self.occupancies[1] |= self.bitboard[i+6]
        self.occupancies[2] = self.occupancies[0] | self.occupancies[1]

        self.en_passant = -1 # case pour manger en passant, si =-1 pas de case

        self.castle_right = 0b1111 #droits au roque
        # 0001 -> le roi blanc peut roquer à l'aile roi
        # 0010 -> le roi blanc peut roquer à l'aile dame
        # 0100 -> le roi noir peut roquer à l'aile roi
        # 1000 -> le roi noir peut roquer à l'aile dame

        self.history = []
        self.history.append((self.bitboard[:], self.occupancies[:], self.side, self.en_passant, self.castle_right))

        self.is_nulle = False
        self.nulle_50_cpt = 0
        self.nulle_3_rep = {}

        # tables d'attaques
        self.pawn_attack = [[], []]
        self.knight_attack = []
        self.king_attack = []
        self.init_leaper_attack()

        self.bishop_attacks = [[0 for _ in range(512)] for _ in range(64)]
        self.rook_attacks = [[0 for _ in range(4096)] for _ in range(64)]
        self.usemagic = True # on utilise ou non le magic bitboard
        self.init_magic_numbers()
        self.init_slider_attack()

        # ZOBRIST HASHING
        self.piece_keys = [[0 for _ in range(64)] for _ in range(12)]
        self.enpassant_keys = [0 for _ in range(64)] # on en aurait besoin que de 8 théoriquement (1 par colonne combinée avec le côté qui joue)
        self.castle_keys = [0 for _ in range(16)]
        self.side_key = 0
        self.hash_hist = [self.position_hash()] # on initialise avec la position 1
        self.init_random_keys()

        self.nulle_3_rep[self.hash_hist[-1]] = 1 # on rajoute la position de départ


    # fonctions sur les bits -----------------------------------------------------------------------

    @staticmethod
    def set_bit(bitboard, case):
        """ bb , int -> bb
        renvoi le bitboard auquel on a mis un 1 sur la case """
        return bitboard | (1 << case)

    @staticmethod
    def pop_bit(bitboard, case):
        """ bb , int -> bb
        renvoi le bitboard auquel on a mis un 0 sur la case """
        return bitboard & ~(1 << case)

    @staticmethod
    def switch_bit(bitboard, case):
        """ U64 , int -> U64
        renvoi le bitboard auquel on a change le bit de la case """
        return bitboard ^ (1 << case)

    @staticmethod
    def get_bit(bitboard, case):
        """ U64 , int -> bool
        renvoi si le bit de la case demandee du bitboard est occupé"""
        return (bitboard & (1 << case) != 0)

    @staticmethod
    def count_bit(bitboard):  # verifier efficacite (static inline equivalent)
        """ U64 -> int
        renvoi le nombre de bit du bitboard """  # TODO: on peut ameliorer la fonction
        bb = bitboard
        count = 0
        while bb:
            count += 1
            bb = bb & (bb-1)  # enleve le bit le moins signifiant
        return count

    @staticmethod
    def ls1b_index(bitboard):  # verifier efficacite (static inline equivalent)
        """ U64 -> int
        renvoi l'index du bit le moins signifiant """  # TODO: on peut ameliorer la fonction
        return Board.count_bit((bitboard & -bitboard)-1)

# AFFICHAGE / DEBUG ######################################################################################

    def print_bb(self, bitboard):
        """ bb -> ()
        affiche le bitboard sous une forme lisible """
        print("val : %s \n" % bitboard)
        for i in range(8):
            ligne = str(8-i)+"   "
            for j in range(8):
                if Board.get_bit(bitboard, 8*i+j):
                    txt = 'x'
                else:
                    txt = '.'
                ligne += txt+" "
            print(ligne)
        print("\n    a b c d e f g h\n")

    def print_board(self,unicode=False):
        """ affiche l'échequier dans la console """

        print()
        for x in range(8):
            ligne = str(8-x)+"   "
            for y in range(8):
                case = x * 8 + y

                char = ""
                for i in range(12):
                    if self.get_bit(self.bitboard[i],case):
                        if unicode:
                            char += PIECE_ASCII[i]
                        else:
                            char += PIECE_LETTER[i]
                if char == "":
                    char = "."
                ligne += char + " "

            print(ligne)
        print("\n    a b c d e f g h\n")
        if self.side:
            print("Trait : Noirs")
        else:
            print("Trait : Blancs")
        if self.en_passant != -1:
            print("En passant : %s"%CASES[self.en_passant])
        print("Droits au roque : %s"%bin(self.castle_right)[2:])
        print("Evaluation côté blanc (en centipions) : %s"%self.evaluation())
        print("Historique schéma : %s"%self.history_debug())

    def is_occupancies_correct(self):
        occ0 = 0
        occ1 = 0
        for i in range(6):
            occ0 |= self.bitboard[i]
            occ1 |= self.bitboard[i+6]
        occ2 = occ0 | occ1
        print(occ0 == self.occupancies[0], occ1 == self.occupancies[1], occ2 == self.occupancies[2])

    # performance test
    def perft(self,depth):
        if depth == 0:
            return 1
        move_list = self.move_generation(self.side)
        somme = 0
        for mv in move_list:
            if self.make_move(mv): # si le coup est legal le fait
                somme += self.perft(depth-1)
                self.undo_move(True)
        return somme

    @staticmethod
    def get_ms():
        return int(round(time.time() * 1000))

    def perft_test(self,depth):
        tic = Board.get_ms()
        print("\n\nProfondeur   Nombres de coups")
        for i in range(1,depth+1):
            print("{0}            {1}".format(i,self.perft(i)))
        tac = Board.get_ms()
        print("\nTemps : %s ms"%(tac-tic))
        print("        %s min"%round((tac-tic)/60000,2))
# performance test

    def set_fen(self,fen):
        '''Update le board en fonction d'un fenboard donné en argument'''

        self.bitboard = [0 for i in range(12)]

        sep_espace = fen.split(' ')
        pieces_par_ligne = sep_espace[0].split('/')
        vide,droits,passant = [str(i+1) for i in range(8)],sep_espace[2],sep_espace[3]

        self.side = (sep_espace[1] == 'b')
        # if sep_espace[1] == 'w':
        #     self.side = WHITE
        # else: self.side = BLACK

        for ligne in range(len(pieces_par_ligne)):
            col = 0
            for piece in pieces_par_ligne[ligne]:
                if piece in vide: # ce n'est pas une piece c'est un nombre
                    col += int(piece)
                else:
                    case = ligne*8 + col
                    elem = PIECE_LETTER.index(piece)
                    self.bitboard[elem] = self.set_bit(self.bitboard[elem], case)
                    col += 1

        self.occupancies = [0,0,0]
        for i in range(6):
            self.occupancies[0] |= self.bitboard[i]
            self.occupancies[1] |= self.bitboard[i+6]
        self.occupancies[2] = self.occupancies[0] | self.occupancies[1]

        if passant == '-':
            self.en_passant = -1 # case pour manger en passant, si =-1 pas de case
        else:
            self.en_passant = CASES.index(passant)

        dico,somme = {'K':1, 'Q':2, 'k':4, 'q':8, '-':0},0
        for s in droits:
            somme += dico[s]
        self.castle_right = somme #droits au roque
        self.add_to_history()
        self.hash_hist.append(self.position_hash()) # on ajoute la position de manière non incrémentale car on recrée une position de 0

    def get_fen(self):
        """Code la position en Notation Forsyth-Edwards"""

        placement_pieces = ''
        for i in range(8): #Pour chaque ligne
            ligne = ''
            vide = 0
            for j in range(8): #Pour chaque colonne
                case,occ_case = 8*i+j,False
                for k in range(12):
                    if self.get_bit(self.bitboard[k],case):
                        if vide != 0:
                            ligne += str(vide)
                        ligne += PIECE_LETTER[k]
                        vide,occ_case = 0,True
                if not(occ_case):
                    vide += 1
            if vide != 0:
                ligne += str(vide)
            placement_pieces += ligne + "/"

        fenboard = placement_pieces[:-1]


        if self.side == WHITE:
            fenboard += ' w '
        else:
            fenboard += ' b '

        droit_aux_roques = ''
        if self.castle_right & 1: # king castling
            droit_aux_roques += 'K'
        if self.castle_right & 2: # queen castling
            droit_aux_roques += 'Q'

        if self.castle_right & 4: # king castling
            droit_aux_roques += 'k'
        if self.castle_right & 8: # queen castling
            droit_aux_roques += 'q'
        fenboard += droit_aux_roques + ' '

        if self.en_passant != -1:
            fenboard += CASES[self.en_passant] + ' '
        else:
            fenboard += '- '
        return fenboard + '0 1' #TODO LE COMPTAGE

    def move_to_pgn(self,move,valid_moves):
        "Prend en entrée un coup et renvoie sa traduction en PGN. Ex : Qxe5+"

        if move.castling:
            if move.target == G1 or move.target == G8:
                return "O-O"
            else: return "O-O-O"

        txt = ''
        piece = move.piece
        case_arrivee = move.target
        case_depart = move.source

        if piece == p or piece == P:
            if move.capture:
                txt += CASES[case_depart][0] + 'x'
        else:
            txt += PIECE_LETTER[piece].upper()
            l,temp = valid_moves,''
            for move_temp in l:
                if move_temp.target == case_arrivee and (move_temp.id != move.id):
                    if move_temp.piece == piece:
                        case_depart_temp = move_temp.source
                        if case_depart_temp//8 == case_depart//8:
                            temp += CASES[case_depart][1]
                        else:
                            temp += CASES[case_depart][0]
            if move.capture:
                temp = 'x' + temp
            txt += temp

        txt2 = ''
        if self.square_is_attacked(self.ls1b_index(self.bitboard[K+self.side*6]),1-self.side):
            txt2 += '+'

        return txt + CASES[case_arrivee] + txt2

    # INITIALISATION DES ATTAQUES ###########################################################################

    def init_leaper_attack(self):
        """ génère les listes d'attaque possible de chaque pièces "sautante" """

        for case in range(64):

            # on initialise les attaques de pion
            self.pawn_attack[0].append(self.mask_pawn_attack(case, WHITE))
            self.pawn_attack[1].append(self.mask_pawn_attack(case, BLACK))

            #on initialise les attaques de cavalier
            self.knight_attack.append(self.mask_knight_attack(case))

            #on initialise les attaques du roi
            self.king_attack.append(self.mask_king_attack(case))

    def init_slider_attack(self):
        """ génère les mouvements des pièces "glissantes" en fonction de leur position et de l'échequier """
        self.bishop_mask = []
        self.rook_mask = []
        self.bishop_attacks = [[0 for _ in range(512)] for _ in range(64)]
        self.rook_attacks = [[0 for _ in range(4096)] for _ in range(64)]

        for case in range(64):
            # on initialise les masks
            self.bishop_mask.append(self.mask_bishop_attack(case))
            self.rook_mask.append(self.mask_rook_attack(case))


            attack_mask1 = self.bishop_mask[case] # pour le fou
            attack_mask2 = self.rook_mask[case] # pour la tour

            # relevant_bits_count1 = self.count_bit(attack_mask1) # pour le fou
            # relevant_bits_count2 = self.count_bit(attack_mask2) # pour la tour
            relevant_bits_count1 = BISHOP_RELEVANT_BITS[case] # pour le fou
            relevant_bits_count2 = ROOK_RELEVANT_BITS[case] # pour la tour

            for i in range(1<<relevant_bits_count1):
                occupancy = self.set_occupancy(i, relevant_bits_count1, attack_mask1)

                magic_index = ((occupancy * self.bishop_magic_numbers[case])&ALL) >> (64-relevant_bits_count1)

                self.bishop_attacks[case][magic_index] = self.bishop_attack_on_the_fly(case,occupancy)
            for i in range(1<<relevant_bits_count2):
                occupancy = self.set_occupancy(i, relevant_bits_count2, attack_mask2)

                magic_index = ((occupancy * self.rook_magic_numbers[case])&ALL) >> (64-relevant_bits_count2)

                self.rook_attacks[case][magic_index] = self.rook_attack_on_the_fly(case,occupancy)

    def get_bishop_attack(self,case,occ,):
        """ renvoi un bitboard de l'attaque du fou en fonction de l'occupance de l'échéquier """
        if self.usemagic:
            id = (((occ & self.bishop_mask[case]) * self.bishop_magic_numbers[case])&ALL) >> (64-BISHOP_RELEVANT_BITS[case])
            return self.bishop_attacks[case][id]
        return self.bishop_attack_on_the_fly(case, occ) # on n'utilise pas le magic bitboard dans ce cas là (peut être utile pour debug)
    def get_rook_attack(self,case,occ):
        """ renvoi un bitboard de l'attaque de la tour en fonction de l'occupance de l'échéquier """
        if self.usemagic:
            id = (((occ & self.rook_mask[case]) * self.rook_magic_numbers[case])&ALL) >> (64-ROOK_RELEVANT_BITS[case])
            return self.rook_attacks[case][id]
        return self.rook_attack_on_the_fly(case, occ) # on n'utilise pas le magic bitboard dans ce cas là (peut être utile pour debug)
    def get_queen_attack(self,case,occ):
        return self.get_bishop_attack(case, occ) | self.get_rook_attack(case, occ)

    # ATTAQUES DES PIECES ###############################################################################

    def mask_pawn_attack(self, case, side):
        """ int , bool -> bb
        renvoi le bitboard de l'attaque du pion situé sur la case passée en argument """

        attack = 0
        bb = Board.set_bit(0, case)  # position du pion en bitboard

        if side == WHITE:
            attack = ((bb & NOT_H_FILE) >> 7) | (
                (bb & NOT_A_FILE) >> 9)
        else:
            attack = ((bb & NOT_A_FILE) << 7) | (
                (bb & NOT_H_FILE) << 9)

        return ALL & attack # evite d'avoir un entier de plus de 64 bit

    def mask_knight_attack(self, case):
        """ int , bool -> bb
        renvoi le bitboard de l'attaque du cavalier situé sur la case passée en argument """

        attack = 0
        bb = Board.set_bit(0, case)  # position du cavalier en bitboard

        attack = (bb & NOT_H_FILE) >> 15
        attack = attack | (bb & NOT_A_FILE) >> 17
        attack = attack | (bb & NOT_AB_FILE) >> 10
        attack = attack | (bb & NOT_GH_FILE) >> 6
        attack = attack | (bb & NOT_A_FILE) << 15
        attack = attack | (bb & NOT_H_FILE) << 17
        attack = attack | (bb & NOT_GH_FILE) << 10
        attack = attack | (bb & NOT_AB_FILE) << 6

        return ALL & attack # evite d'avoir un entier de plus de 64 bit

    def mask_king_attack(self, case):
        """ int , bool -> bb
        renvoi le bitboard de l'attaque du roi situé sur la case passée en argument """

        attack = 0
        bb = Board.set_bit(0, case)  # position du roi en bitboard

        attack = bb >> 8 | bb << 8
        if bb & NOT_A_FILE:
            attack = attack | bb >> 1 | bb >> 9 | bb << 7
        if bb & NOT_H_FILE:
            attack = attack | bb << 1 | bb << 9 | bb >> 7

        return ALL & attack # evite d'avoir un entier de plus de 64 bit

    def mask_bishop_attack(self, case):
        """ int , bool -> U64
        renvoi le bitboard de l'attaque du fou situé sur la case passée en argument """

        attack = 0

        rank, file = case//8, case % 8  # ligne et colonne de la pieces
        for i in range(1, min(7-rank, 7-file)):
            r, f = rank+i, file+i
            attack = attack | 1 << (r*8 + f)
        for i in range(1, min(rank, file)):
            r, f = rank-i, file-i
            attack = attack | 1 << (r*8 + f)
        for i in range(1, min(7-rank, file)):
            r, f = rank+i, file-i
            attack = attack | 1 << (r*8 + f)
        for i in range(1, min(rank, 7-file)):
            r, f = rank-i, file+i
            attack = attack | 1 << r*8 + f

        return attack

    def mask_rook_attack(self, case):
        """ int , bool -> U64
        renvoi le bitboard de l'attaque de la tour situé sur la case passée en argument """

        attack = 0

        rank, file = case//8, case % 8  # ligne et colonne de la pieces
        for i in range(1, 7-rank):
            r, f = rank+i, file
            attack = attack | 1 << (r*8 + f)
        for i in range(1, rank):
            r, f = rank-i, file
            attack = attack | 1 << (r*8 + f)
        for i in range(1, 7-file):
            r, f = rank, file+i
            attack = attack | 1 << (r*8 + f)
        for i in range(1, file):
            r, f = rank, file-i
            attack = attack | 1 << (r*8 + f)

        return attack

    # PIECES GLISSANTES (sliding pieces) "on the fly" #####################################

    def bishop_attack_on_the_fly(self, case, block):
        """ renvoi le bitboard de l'attaque du fou en prenant en compte les pieces présente """
        attack = 0

        rank, file = case//8, case % 8  # ligne et colonne de la pieces
        for i in range(1, min(8-rank, 8-file)):
            r, f = rank+i, file+i
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur
        for i in range(1, min(rank+1, file+1)):
            r, f = rank-i, file-i
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur
        for i in range(1, min(8-rank, file+1)):
            r, f = rank+i, file-i
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur
        for i in range(1, min(rank+1, 8-file)):
            r, f = rank-i, file+i
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur

        return attack

    def rook_attack_on_the_fly(self, case, block):
        """ renvoi le bitboard de l'attaque de la tour en prenant en compte les pieces présente """
        attack = 0

        rank, file = case//8, case % 8  # ligne et colonne de la pieces
        for i in range(1, 8-rank):
            r, f = rank+i, file
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur
        for i in range(1, rank+1):
            r, f = rank-i, file
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur
        for i in range(1, 8-file):
            r, f = rank, file+i
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur
        for i in range(1, file+1):
            r, f = rank, file-i
            b = 1 << (r*8 + f)
            attack = attack | b
            if b & block:
                break  # on sors de la boucle si on rencontre un bloqueur

        return attack

    # test si une case est attaquée #######################################################

    def square_is_attacked(self,case,side):
        """ int, bool -> bool
            renvoi vrai si la case est attaqué par le coté choisi """
        if side == WHITE:
            if (self.pawn_attack[BLACK][case] & self.bitboard[P]): return True
            if (self.knight_attack[case] & self.bitboard[N]): return True
            if (self.king_attack[case] & self.bitboard[K]): return True
            if (self.get_bishop_attack(case, self.occupancies[2]) & (self.bitboard[B] | self.bitboard[Q])): return True
            if (self.get_rook_attack(case, self.occupancies[2]) & (self.bitboard[R] | self.bitboard[Q])): return True
            return False
        else:
            if (self.pawn_attack[WHITE][case] & self.bitboard[p]): return True
            if (self.knight_attack[case] & self.bitboard[n]): return True
            if (self.king_attack[case] & self.bitboard[k]): return True
            if (self.get_bishop_attack(case, self.occupancies[2]) & (self.bitboard[b] | self.bitboard[q])): return True
            if (self.get_rook_attack(case, self.occupancies[2]) & (self.bitboard[r] | self.bitboard[q])): return True

            return False

    def attacked_bitboard(self,side):
        bb = 0
        for i in range(8):
            for j in range(8):
                if self.square_is_attacked(8*i+j,side):
                    bb = Board.set_bit(bb, 8*i+j)
        return bb


    ######################################################################################
    # // GENERATION DES COUPS // #########################################################
    ######################################################################################

    def move_generation(self,side):
        """ génère les coups pseudo légaux possibles du côté donné en argument """

        move_list = [] #liste des pseudo coups possibles encodé selon la forme d'au dessus

        # castling rights
        if side == WHITE:
            if self.castle_right & 1: # king castling
                if not (self.occupancies[2] & (2**F1 + 2**G1)):
                    if (not self.square_is_attacked(E1, BLACK)) and (not self.square_is_attacked(F1, BLACK)):
                        move_list.append(Move(E1, G1, K, NO_PIECE, 0, 0, 0, 1))
            if self.castle_right & 2: # queen castling
                if not (self.occupancies[2] & (2**D1 + 2**C1 + 2**B1)):
                    if (not self.square_is_attacked(E1, BLACK)) and (not self.square_is_attacked(D1, BLACK)):
                        move_list.append(Move(E1, C1, K, NO_PIECE, 0, 0, 0, 1))
        else:
            if self.castle_right & 4: # king castling
                if not (self.occupancies[2] & (2**F8 + 2**G8)):
                    if (not self.square_is_attacked(E8, WHITE)) and (not self.square_is_attacked(F8, WHITE)):
                        move_list.append(Move(E8, G8, k, NO_PIECE, 0, 0, 0, 1))
            if self.castle_right & 8: # queen castling
                if not (self.occupancies[2] & (2**D8 + 2**C8 + 2**B8)):
                    if (not self.square_is_attacked(E8, WHITE)) and (not self.square_is_attacked(D8, WHITE)):
                        move_list.append(Move(E8, C8, k, NO_PIECE, 0, 0, 0, 1))

        for piece in range(side*6,(side+1)*6): # on selectionne la bonne partie de bitboard en fonction du side
            bb = self.bitboard[piece]

            if piece == P : # pion blanc
                while bb:
                    depart = self.ls1b_index(bb)
                    bb = self.pop_bit(bb, depart) # on enlève la case de départ afin de regarder ensuite les suivantes

                    # attaque de pion
                    is_attacking = self.pawn_attack[0][depart] & self.occupancies[1]
                    while is_attacking:
                        arrivee = self.ls1b_index(is_attacking)
                        if arrivee <= H8: #on mange et on promotionne
                            move_list.insert(0,Move(depart, arrivee, P, Q, 1, 0, 0, 0))
                            move_list.insert(0,Move(depart, arrivee, P, R, 1, 0, 0, 0))
                            move_list.insert(0,Move(depart, arrivee, P, B, 1, 0, 0, 0))
                            move_list.insert(0,Move(depart, arrivee, P, N, 1, 0, 0, 0))
                        else:
                            move_list.insert(0,Move(depart,arrivee,P,NO_PIECE,1,0,0,0))
                        is_attacking = self.pop_bit(is_attacking, arrivee)

                    # prise en passant
                    if self.en_passant != -1 and (self.pawn_attack[0][depart] & (1<<self.en_passant)):
                        move_list.insert(0,Move(depart, self.en_passant, P, NO_PIECE, 1, 0, 1, 0))

                    # coup de pion blanc discret
                    arrivee = depart - 8
                    if arrivee>= A8 and not self.get_bit(self.occupancies[2],arrivee):

                        #promotion
                        if arrivee <= H8: #le pion arrive sur la dernière rangée
                            move_list.append(Move(depart,arrivee,P,Q,0,0,0,0))
                            move_list.append(Move(depart,arrivee,P,R,0,0,0,0))
                            move_list.append(Move(depart,arrivee,P,B,0,0,0,0))
                            move_list.append(Move(depart,arrivee,P,N,0,0,0,0))
                        else:
                            # avancée de 2 cases
                            if (A2 <= depart <= H2) and not self.get_bit(self.occupancies[2],arrivee-8):
                                move_list.append(Move(depart,arrivee-8,P,NO_PIECE,0,1,0,0))
                            move_list.append(Move(depart,arrivee,P,NO_PIECE,0,0,0,0))
            elif piece == p : # pion noir
                while bb:
                    depart = self.ls1b_index(bb)
                    bb = self.pop_bit(bb, depart) # on enlève la case de départ afin de regarder ensuite les suivantes

                    # attaque de pion
                    is_attacking = self.pawn_attack[1][depart] & self.occupancies[0]
                    while is_attacking:
                        arrivee = self.ls1b_index(is_attacking)
                        if arrivee >= A1: #on mange et on promotionne
                            move_list.insert(0,Move(depart, arrivee, p, q, 1, 0, 0, 0))
                            move_list.insert(0,Move(depart, arrivee, p, r, 1, 0, 0, 0))
                            move_list.insert(0,Move(depart, arrivee, p, b, 1, 0, 0, 0))
                            move_list.insert(0,Move(depart, arrivee, p, n, 1, 0, 0, 0))
                        else:
                            move_list.insert(0,Move(depart, arrivee, p, NO_PIECE, 1, 0, 0, 0))

                        is_attacking = self.pop_bit(is_attacking, arrivee)
                    # prise en passant
                    if self.en_passant != -1 and (self.pawn_attack[1][depart] & (1<<self.en_passant)):
                        move_list.insert(0,Move(depart, self.en_passant, p, NO_PIECE, 1, 0, 1, 0))

                    # coup de pion noir discret
                    arrivee = depart + 8 # + pour noir - pour blanc
                    if arrivee <= H1 and not self.get_bit(self.occupancies[2],arrivee):

                        #promotion
                        if arrivee >= A1: #le pion arrive sur la dernière rangée
                            move_list.append(Move(depart,arrivee,p,q,0,0,0,0))
                            move_list.append(Move(depart,arrivee,p,r,0,0,0,0))
                            move_list.append(Move(depart,arrivee,p,b,0,0,0,0))
                            move_list.append(Move(depart,arrivee,p,n,0,0,0,0))
                        else:
                            # avancée de 2 cases
                            if (A7 <= depart <= H7) and not self.get_bit(self.occupancies[2],arrivee+8):
                                move_list.append(Move(depart,arrivee+8,p,NO_PIECE,0,1,0,0))
                            move_list.append(Move(depart,arrivee,p,NO_PIECE,0,0,0,0))
            else: #autres pièces
                while bb:
                    depart = self.ls1b_index(bb)
                    bb = self.pop_bit(bb, depart) # on enlève la case de départ afin de regarder ensuite les suivantes
                    if piece in [K,k]:
                        attack_map = self.king_attack[depart] & ~(self.occupancies[side]) # on ne regarde pas les cases où il y a nos propres pieces puisqu'on ne peut pas y aller.
                    elif piece in [N,n]:
                        attack_map = self.knight_attack[depart] & ~(self.occupancies[side])
                    elif piece in [B,b]:
                        attack_map = self.get_bishop_attack(depart, self.occupancies[2]) & ~(self.occupancies[side])
                    elif piece in [R,r]:
                        attack_map = self.get_rook_attack(depart, self.occupancies[2]) & ~(self.occupancies[side])
                    else:
                        attack_map = self.get_queen_attack(depart, self.occupancies[2]) & ~(self.occupancies[side])
                    while attack_map:
                        arrivee = self.ls1b_index(attack_map)
                        attack_map = self.pop_bit(attack_map, arrivee)
                        if self.get_bit(self.occupancies[2], arrivee): # il y a une prise
                            move_list.insert(0,Move(depart, arrivee, piece, NO_PIECE, 1, 0, 0, 0)) #on met les captures au début de la liste
                        else:
                            move_list.append(Move(depart, arrivee, piece, NO_PIECE, 0, 0, 0, 0))


        return move_list

    def legal_move_generation(self,side):
        liste = self.move_generation(side)
        L = []
        for move in liste:
            if self.make_move(move):
                L.append(move)
                self.undo_move(True)
        # print(L)
        return L


    def print_move(self,side,legal=True):
        if legal:
            liste = self.legal_move_generation(side)
        else:
            liste = self.move_generation(side)
        print("\n")
        print("Coup   Piece  Capture  Double  Enpassant  Roque")
        print()
        for move in liste:
            coup = CASES[move.source] + CASES[move.target] + PIECE_LETTER[move.promotion].lower()
            piece = PIECE_LETTER[move.piece]
            capt = int(move.capture)
            double = int(move.double)
            enpass = int(move.enpassant)
            roque = int(move.castling)
            print("{0}  {1}      {2}        {3}       {4}          {5}".format(coup,piece,capt,double,enpass,roque))
        print("\nNombre de coup : %s"%len(liste))


    ############################################################################################################################################
    ##### // MAKE MOVE and UNDO MOVE FUNCTIONS // ##############################################################################################
    ############################################################################################################################################

    def add_to_history(self):
        """ ajoute la position actuelle à l'historique """
        self.history.append((self.bitboard[:], self.occupancies[:], self.side, self.en_passant, self.castle_right))


    def history_debug(self):
        L = []
        id = -1
        last_pos = ([],[],0,0,0)
        for pos in self.history:
            # print(pos)
            if pos != last_pos:
                id += 1
                last_pos = pos
            L.append(id)
        return L

    def undo_move(self, real_move):
        """ annule le dernier coup, si real_move = True alors on supprime d'abord la dernière entrée de l'historique sinon non """
        self.is_nulle = False
        if real_move and len(self.history) >= 2:
            self.nulle_3_rep[self.hash_hist[-1]] = max(self.nulle_3_rep[self.hash_hist[-1]]-1,0)
            del self.history[-1]
            del self.hash_hist[-1]
        (bb, occ, sd, enpass, castle) = self.history[-1]
        self.bitboard = bb[:]
        self.occupancies = occ[:]
        self.en_passant = enpass
        self.castle_right = castle
        self.side = sd

    def make_move(self, move, only_capture_flag=False):
        """ fait le coup et l'ajoute à l'historique """

        if (only_capture_flag and not move.capture) or self.nulle_50_cpt >= 50 or self.is_nulle:
            return 0 # on ne fait pas le coup

        hash = self.hash_hist[-1] # on récupère le hash de la position avant le coup

        # on récupère les informations du coup
        source = move.source
        target = move.target
        piece = move.piece
        promote = move.promotion
        capture = move.capture
        double = move.double
        enpass = move.enpassant
        roque = move.castling

        cpt_sauv = self.nulle_50_cpt
        if capture or piece in [P,p]:
            self.nulle_50_cpt = 0
        else:
            self.nulle_50_cpt += 1 # on rajoute un coup au compteur

        # on déplace la pièce
        self.bitboard[piece] = self.pop_bit(self.bitboard[piece], source)
        hash ^= self.piece_keys[piece][source] # on enlève la piece de la case de départ

        if promote != NO_PIECE: # si il y a une promotion
            self.bitboard[promote] = self.set_bit(self.bitboard[promote], target)
            hash ^= self.piece_keys[promote][target] # on rajoute la promotion sur la case d'arrivée
        else:
            self.bitboard[piece] = self.set_bit(self.bitboard[piece], target)
            hash ^= self.piece_keys[piece][target] # on rajoute la piece sur la case d'arrivée

        self.occupancies[self.side] = self.pop_bit(self.occupancies[self.side], source)
        self.occupancies[self.side] = self.set_bit(self.occupancies[self.side], target)
        self.occupancies[2] = self.pop_bit(self.occupancies[2], source) # quel que soit le coup il n'y aura plus de piece sur la case d'origine

        # on gère les captures
        if enpass: # cas particulier : prise en passant
            if self.side == WHITE:
                self.bitboard[p] = self.pop_bit(self.bitboard[p], target+8)
                hash ^= self.piece_keys[p][target+8]

                self.occupancies[1] = self.pop_bit(self.occupancies[1], target+8) # on retire la piece de l'occupance global de la couleur attaquée
                self.occupancies[2] = self.pop_bit(self.occupancies[2], target+8)
                self.occupancies[2] = self.set_bit(self.occupancies[2], target)
            else:
                self.bitboard[P] = self.pop_bit(self.bitboard[P], target-8)
                hash ^= self.piece_keys[P][target-8]

                self.occupancies[0] = self.pop_bit(self.occupancies[0], target-8) # on retire la piece de l'occupance global de la couleur attaquée
                self.occupancies[2] = self.pop_bit(self.occupancies[2], target-8)
                self.occupancies[2] = self.set_bit(self.occupancies[2], target)

        if capture:
            self.occupancies[1-self.side] = self.pop_bit(self.occupancies[1-self.side], target) # on retire la piece de l'occupance global de la couleur attaquée

            for i in range((1-self.side)*6,(2-self.side)*6): # on parcours les pieces de la couleur adverse
                if self.get_bit(self.bitboard[i], target):
                    self.bitboard[i] = self.pop_bit(self.bitboard[i], target)
                    hash ^= self.piece_keys[i][target] # on efface la piece capturée
                    break
        else:
            self.occupancies[2] = self.set_bit(self.occupancies[2], target) # il n'y avait pas de piece avant donc on doit l'ajouter


        if self.en_passant != -1: hash ^= self.enpassant_keys[self.en_passant] # on enlève potentiellement la dernière case de en passant
        if double: # on défini la nouvelle case de en passant
            self.en_passant = source + (-1 + 2*self.side)*8
            hash ^= self.enpassant_keys[self.en_passant] # on rajoute la case en passant dans le hash
        else:
            self.en_passant = -1

        hash ^= self.castle_keys[self.castle_right] # on enlève l'ancien castle rigth
        if roque: # on doit deplacer la tour et enlever le droit au roque
            if target == G1:
                self.bitboard[R] = self.set_bit(self.bitboard[R], F1)
                hash ^= self.piece_keys[R][F1]
                self.bitboard[R] = self.pop_bit(self.bitboard[R], H1)
                hash ^= self.piece_keys[R][H1]
                self.occupancies[0] = self.set_bit(self.occupancies[0], F1)
                self.occupancies[0] = self.pop_bit(self.occupancies[0], H1)
                self.occupancies[2] = self.set_bit(self.occupancies[2], F1)
                self.occupancies[2] = self.pop_bit(self.occupancies[2], H1)
                self.castle_right &= 0b1100
            elif target == C1:
                self.bitboard[R] = self.set_bit(self.bitboard[R], D1)
                hash ^= self.piece_keys[R][D1]
                self.bitboard[R] = self.pop_bit(self.bitboard[R], A1)
                hash ^= self.piece_keys[R][A1]
                self.occupancies[0] = self.set_bit(self.occupancies[0], D1)
                self.occupancies[0] = self.pop_bit(self.occupancies[0], A1)
                self.occupancies[2] = self.set_bit(self.occupancies[2], D1)
                self.occupancies[2] = self.pop_bit(self.occupancies[2], A1)
                self.castle_right &= 0b1100
            elif target == G8:
                self.bitboard[r] = self.set_bit(self.bitboard[r], F8)
                hash ^= self.piece_keys[r][F8]
                self.bitboard[r] = self.pop_bit(self.bitboard[r], H8)
                hash ^= self.piece_keys[r][H8]
                self.occupancies[1] = self.set_bit(self.occupancies[0], F8)
                self.occupancies[1] = self.pop_bit(self.occupancies[0], H8)
                self.occupancies[2] = self.set_bit(self.occupancies[2], F8)
                self.occupancies[2] = self.pop_bit(self.occupancies[2], H8)
                self.castle_right &= 0b0011
            else:
                self.bitboard[r] = self.set_bit(self.bitboard[r], D8)
                hash ^= self.piece_keys[r][D8]
                self.bitboard[r] = self.pop_bit(self.bitboard[r], A8)
                hash ^= self.piece_keys[r][A8]
                self.occupancies[1] = self.set_bit(self.occupancies[1], D8)
                self.occupancies[1] = self.pop_bit(self.occupancies[1], A8)
                self.occupancies[2] = self.set_bit(self.occupancies[2], D8)
                self.occupancies[2] = self.pop_bit(self.occupancies[2], A8)
                self.castle_right &= 0b0011
        elif piece == K:
            self.castle_right &= 0b1100
        elif piece == k:
            self.castle_right &= 0b0011

        # on update les droits aux roques si une tour bouge ou si elle est capturée
        if (piece == R and source == H1) or target == H1:
            self.castle_right &= 0b1110
        elif (piece == R and source == A1) or target == A1:
            self.castle_right &= 0b1101
        elif (piece == r and source == H8) or target == H8:
            self.castle_right &= 0b1011
        elif (piece == r and source == A8) or target == A8:
            self.castle_right &= 0b0111
        hash ^= self.castle_keys[self.castle_right] # on ajoute le nouveau castle right

        #on vérifie si le roi n'est pas en échec
        if self.square_is_attacked(self.ls1b_index(self.bitboard[K+6*self.side]), 1^self.side):
            self.undo_move(False)
            self.nulle_50_cpt -= cpt_sauv
            return 0 # le coup est illegal

        # on finalise le coup
        self.side ^= 1 # on change de coté
        hash ^= self.side_key # on change de côté

        self.add_to_history()

        self.hash_hist.append(self.position_hash()) # pas le plus oti mais le hashing incrémental marche pas pour l'instant
        # self.hash_hist.append(hash) # on rajoute la nouvelle position à l'historique des hashs
        # if hash != self.position_hash():
        #     print("!!! erreur dans le hashing incrémental !!!")
        #     print("coup : %s\n"%move.txt())
        if not self.hash_hist[-1] in self.nulle_3_rep:
            self.nulle_3_rep[self.hash_hist[-1]] = 1
        else:
            self.nulle_3_rep[self.hash_hist[-1]] += 1
            if self.nulle_3_rep[self.hash_hist[-1]] >= 3:
                self.is_nulle = True

        return 1 # le coup est legal



    ##########################################################################################
    #### FONCTION D'EVALUATION ###############################################################
    ##########################################################################################

    def naive_eval(self):
        """ fonction d'évaluation naive pour le debug (ne prend que la valeur des pieces en compte)"""
        val = 0
        for piece in range(12):
            bb = self.bitboard[piece]
            while bb:
                case = self.ls1b_index(bb)
                bb = self.pop_bit(bb, case)
                val += PIECE_VAL[piece]

        if self.side == WHITE:
            return val
        else:
            return -val

    def evaluation(self,absolute=True):
        """ Renvoie l'évaluation de la position actuelle
            absolute determine si on doit prendre la valeur opposée si ce sont les noirs qui jouent

            material [t] [mg|eg|ph] Material score, where each piece on the board has a predefined value
                                    that changes depending on the phase of the game.
            imbalance [t] [mg|eg|ph] Imbalance score that compares the piece count of each piece type for both
                                        colours. E.g., it awards having a pair of bishops vs a bishop and a knight.
            pawns [t] [mg|eg|ph] Evaluation of the pawn structure. E.g., the evaluation considers isolated,
                                    double, connected, backward, blocked, weak, etc. pawns.
            knights [t] [mg|eg|ph] Evaluation of knights. E.g., extra points are given to knights
                                    that occupy outposts protected by pawns.
            bishops [t] [mg|eg|ph] Evaluation of bishops. E.g., bishops that occupy the same color squares
                                    as pawns are penalised.
            rooks [t] [mg|eg|ph] Evaluation of rooks. E.g., rooks that occupy open or semi-open files
                                    have higher valuation.
            queens [t] [mg|eg|ph] Evaluation of queens. E.g., queens that have relative pin or discovered
                                    attack against them are penalized.
            mobility [t] [mg|eg|ph] Evaluation of piece mobility score. It depends on
                                    the number of squares attacked by the pieces.
            king_safety [t] [mg|eg|ph] A complex concept related to king safety. It depends on the number
                                        and type of pieces that attack squares around the king, shelter strength,
                                        number of pawns around the king, penalties for being on pawnless flank, etc.
            threats [t] [mg|eg|ph] Evaluation of threats to pieces, such as whether a pawn can safely advance
                                    and attack an opponent’s higher value piece, hanging pieces,
                                    possible xray attacks by rooks, etc.
            passed_pawns [t] [mg|eg|ph] Evaluates bonuses for passed pawns. The closer a pawn is to the promotion
                                        rank, the higher is the bonus.
            space [t] [mg|eg|ph] Evaluation of the space. It depends on the number of safe squares available
                                    for minor pieces on the central four files on ranks 2 to 4.
            total [t] [mg|eg|ph] The total evaluation of a given position. It encapsulates all the above concepts."""


        val = 0
        foub = 0
        foun = 0
        piece_restantes = 0

        white_pawn_struct = []
        black_pawn_struct = []
        for col in range(8):
            white_pawn_struct.append(self.count_bit(FILE[col]&self.bitboard[P]))
            black_pawn_struct.append(self.count_bit(FILE[col]&self.bitboard[p]))

        for nb in white_pawn_struct:
            if nb >= 2:
                val -= 10*nb
        for nb in black_pawn_struct:
            if nb >= 2:
                val += 10*nb


        for piece in range(12):
            bb = self.bitboard[piece]
            while bb:
                piece_restantes += 1
                case = self.ls1b_index(bb)
                bb = self.pop_bit(bb, case)
                val += PIECE_VAL[piece]
                if piece < 6: # piece blanche
                    val += POS_SCORE[piece][case]
                else:
                    val -= POS_SCORE[piece-6][MIRROR_CASE[case]]

                if piece == B: # gérer les paires de fou
                    foub += 1
                elif piece == b:
                    foun += 1
                elif piece == R:
                    if not white_pawn_struct[case % 8]: # si il n'y a pas de pion blanc sur la colonne
                        val += 30
                        if not black_pawn_struct[case % 8]:
                            val += 20
                elif piece == r:
                    if not black_pawn_struct[case % 8]: # si il n'y a pas de pion blanc sur la colonne
                        val -= 30
                        if not white_pawn_struct[case % 8]:
                            val -= 20
                elif piece == K and not white_pawn_struct[case % 8]: # roi sur colonne ouverte
                    val -= 150
                elif piece == k and not black_pawn_struct[case % 8]: # roi sur colonne ouverte
                    val += 150

        if foub >= 2:
            val += 40
        if foun >= 2:
            val -= 40

        if absolute or self.side == WHITE:
            return val
        else:
            return -val


    ############################################################################
    #### CONNECTIONS A L'INTERFACE #############################################
    ############################################################################

    def trad_move(self,string):
        """ traduit le coup pour pouvoir l'utiliser """
        move_list = self.legal_move_generation(self.side)
        if move_list == []:
            print("nulle ou mat !")

        source = CASES.index(string[0:2].lower())
        target = CASES.index(string[2:4].lower())
        prom = string[4]
        if self.side == WHITE:
            promotion = PIECE_LETTER.index(prom.upper())
        else:
            promotion = PIECE_LETTER.index(prom.lower())
        for move in move_list:
            if source == move.source and target == move.target and promotion == move.promotion:
                return move
        # le coup est incorrect ou laisse le roi en echec
        return -1

    ###################################################################################
    # MAGIC NUMBER ####################################################################
    ##################################################################################

    def set_occupancy(self, index, bits_in_mask, attack_mask):
        """ renvoi un bitboard de l'attack_mask auquel on a enlevé quelques cases en fonction de l'index """
        occupancy = 0
        attack_map = attack_mask

        for i in range(bits_in_mask):
            square = Board.ls1b_index(attack_map)
            attack_map = Board.pop_bit(attack_map, square)

            if index & (1 << i):
                occupancy = occupancy | (1 << square)

        return occupancy



    def find_magic_number(self, square, relevant_bits, isbishop):
        """ génère un magic number correct par force brute"""

        occupancies = [0 for _ in range(4096)]
        attacks = [0 for _ in range(4096)]

        attack_mask = 0
        if isbishop:
            attack_mask = self.mask_bishop_attack(square)
        else:
            attack_mask = self.mask_rook_attack(square)

        occupancy_index = 1 << relevant_bits
        for i in range(occupancy_index):
            occupancies[i] = self.set_occupancy(i, relevant_bits, attack_mask)

            if isbishop:
                attacks[i] = self.bishop_attack_on_the_fly(
                    square, occupancies[i])
            else:
                attacks[i] = self.rook_attack_on_the_fly(
                    square, occupancies[i])
        # test de possible magic number
        for rdcount in range(10000000): #100000000
            magic_number = generate_magic_number()

            # on passe les mauvais magic number sûr
            if self.count_bit((attack_mask * magic_number) & 18374686479671623680) < 6:
                continue

            used_attacks = [0 for _ in range(4096)]

            index = 0
            fail = False
            while index < occupancy_index and not fail:
                magic_index = ((occupancies[index] * magic_number)&ALL) >> (64-relevant_bits)
                # print("magic_index : %s"%magic_index)
                if used_attacks[magic_index] == 0:
                    used_attacks[magic_index] = attacks[index]
                # le magic number ne marche pas !
                elif used_attacks[magic_index] != attacks[index]:
                    fail = True
                index += 1

            if not fail:  # le nombre est bien un magic number !
                return magic_number

        print('magic number non trouvé !')
        return 0


    def init_magic_numbers(self):
        """ initialise les magic numbers pour chaque pièces et chaque cases """

        # self.bishop_magic_numbers = []
        # self.rook_magic_numbers = []
        #
        # for case in range(64):
        #     #magic number pour le fou
        #     self.bishop_magic_numbers.append(self.find_magic_number(case, BISHOP_RELEVANT_BITS[case], True))
        #     print("%s,"%self.bishop_magic_numbers[case])
        # print('\n ------------------------- \n -------------------------------- \n')
        # for case in range(64):
        #     #magic number pour la tour
        #     self.rook_magic_numbers.append(self.find_magic_number(case, ROOK_RELEVANT_BITS[case], False))
        #     print("%s,"%self.rook_magic_numbers[case])
        #
        # print(len(self.bishop_magic_numbers),len(self.rook_magic_numbers))

        self.bishop_magic_numbers = [
        1189799142386565152,
        20345365374976064,
        4508136459208704,
        1154052910864269316,
        55257331318916480,
        11718509236722870289,
        9223464473678906563,
        10152924764701824,
        437429843567607953,
        9223389912643469352,
        74599674589347968,
        708103213547664,
        4415763253410,
        1157443802912292872,
        108087492852320258,
        17768833884160,
        2396477969708227072,
        2486552160532440064,
        308496643198554144,
        158189074895605761,
        1126044125890644,
        94716333966540802,
        437412253529081860,
        2315272429558598176,
        1191237291230888192,
        238708442314051712,
        10382081371341340688,
        18018797684326432,
        4756368555073634816,
        72341268051006466,
        290483275753883668,
        546101313325367832,
        1128134502060192,
        9232959932887728416,
        577023908419600513,
        11529813214753784070,
        598701261324320,
        3557852502789491712,
        2452922694312788480,
        19153493092761760,
        4648286579746440770,
        10276041578909872,
        13835906886865650180,
        299342313310725,
        9234635502831799296,
        15064575940176691456,
        5246835957272971012,
        5192654769482891396,
        576602057266463264,
        200551505043918978,
        154652917760,
        9148006570000386,
        14126688534245163524,
        4899951615494595328,
        18157344218218496,
        217299798729035778,
        2595763351934222850,
        729904336683960368,
        648664170149187586,
        36172835462447648,
        654436607802344587,
        306245359063015554,
        3535343437245104256,
        565303796990464
        ]
        self.rook_magic_numbers = [
        1188950861045339168,
        18014467231055936,
        8394744890059262080,
        2341889398553052288,
        4647717564292532224,
        1188951409727635584,
        9367489423962342408,
        144121815212508292,
        140738033631236,
        1153203121321672840,
        576742296536547392,
        9512869084762473601,
        141287311280128,
        2814819091092992,
        3377983323636865,
        146929955031238922,
        53326318141576,
        2310347984304349184,
        9223514424415887360,
        141287512606720,
        9226469361383180288,
        20408585179628544,
        2305988144769667080,
        288232575314694281,
        36099180795887648,
        721209268742656002,
        17594335625344,
        4614280868021666432,
        9295711677100589072,
        720580340581663232,
        8813272957456,
        1297037251028472068,
        2882444773908545632,
        90072269581197322,
        580964523731584001,
        5837828400542138384,
        4613379268490037248,
        4644345714050048,
        9804513478944227864,
        2882313108607472673,
        598958984560640,
        1306044167083802656,
        4503737070584064,
        2472486091299553312,
        6989595417839173760,
        577023736683823120,
        11261198158856448,
        1225053866518249481,
        2359886480165306496,
        2594399473241227520,
        648659771059077760,
        4634204085417967744,
        2306423568667312384,
        1154049605684691072,
        3035428416607749120,
        9585441783404349952,
        324841919788155010,
        12971002582314058242,
        6016528702032129,
        9223407255654760705,
        9377058611157012482,
        2533310290985537,
        299110133924004,
        108122126260700178
        ]

    ##########################################################################################################################
    ########### ZOBRIST HASHING ##############################################################################################
    ##########################################################################################################################

    """ !!! ATTENTION UNDO_MOVE MODIFIE HASH_HIST MAIS PAS ADD_TO_HISTORY (c'est make_move qui le fait) """

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


    def position_hash(self):
        """ génère un hash de la position à partir du départ """
        hash = 0
        hash ^= self.castle_keys[self.castle_right]
        if self.en_passant != -1:
            hash ^= self.enpassant_keys[self.en_passant]
        if self.side:
            hash ^= self.side_key
        for piece in range(12):
            bb = self.bitboard[piece]
            while bb:
                case = self.ls1b_index(bb)
                bb = self.pop_bit(bb,case)
                hash ^= self.piece_keys[piece][case]
        return hash
