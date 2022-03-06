# -*- coding: utf-8 -*-
"""
Created on Mon Feb  21 12:35:18 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

BOARD
"""

from init import *

class Board:
    """ classe qui gère tout l'échéquier """

    def __init__(self):
        self.init()

    def init(self):
        """ initialise l'échéquier """

        self.side = WHITE

        self.bitboard = [
            71776119061217280,
            2**60,
            2**59,
            2**58+2**61,
            2**57+2**62,
            2**56+2**63,
            65280,
            2**4,
            2**3,
            2**2+2**5,
            2**1+2**6,
            2**0+2**7
            ]
        self.occupancies = [0,0,0]
        for i in range(6):
            self.occupancies[0] |= self.bitboard[i]
            self.occupancies[1] |= self.bitboard[i+6]
        self.occupancies[2] = self.occupancies[0] | self.occupancies[1]

        self.en_passant = -1 # case pour manger en passant, si =-1 pas de case

        self.castle_right = int("0b1111",base = 2) #droits au roque
        # 0001 -> le roi blanc peut roquer à l'aile roi
        # 0010 -> le roi blanc peut roquer à l'aile dame
        # 0100 -> le roi noir peut roquer à l'aile roi
        # 1000 -> le roi noir peut roquer à l'aile dame

        self.history = []
        self.history.append((self.bitboard[:], self.occupancies[:], self.en_passant, self.castle_right))

        # tables d'attaques
        self.pawn_attack = [[], []]
        self.knight_attack = []
        self.king_attack = []
        self.init_leaper_attack()

        self.bishop_attacks = [[0 for _ in range(512)] for _ in range(64)]
        self.rook_attacks = [[0 for _ in range(4096)] for _ in range(64)]
        # self.init_magic_numbers()
        # self.init_slider_attack()



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
        """ U64 , int -> U64
        renvoi le bit de la case demandee du bitboard """
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
            print("En passant : %s"%self.case_int2str(self.en_passant))
        print("Droits au roque : %s"%bin(self.castle_right)[2:])

    def is_occupancies_correct(self):
        occ0 = 0
        occ1 = 0
        for i in range(6):
            occ0 |= self.bitboard[i]
            occ1 |= self.bitboard[i+6]
        occ2 = occ0 | occ1
        print(occ0 == self.occupancies[0], occ1 == self.occupancies[1], occ2 == self.occupancies[2])

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



    def get_bishop_attack(self,case,occ):
        """ renvoi un bitboard de l'attaque du fou en fonction de l'occupance de l'échéquier """
        # bb = U64((occ & self.bishop_mask[case]) * self.bishop_magic_numbers[case]) >> U64(64-self.bishop_relevant_bits[case])
        # return self.bishop_attacks[case][bb]
        return self.bishop_attack_on_the_fly(case, occ)
    def get_rook_attack(self,case,occ):
        """ renvoi un bitboard de l'attaque de la tour en fonction de l'occupance de l'échéquier """
        # bb = U64((occ & self.rook_mask[case]) * self.rook_magic_numbers[case]) >> U64(64-self.rook_relevant_bits[case])
        # return self.rook_attacks[case][bb]
        return self.rook_attack_on_the_fly(case, occ)
    def get_queen_attack(self,case,occ):
        return self.get_bishop_attack(case,occ) | self.get_rook_attack(case, occ)

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

        attack = U64(0)

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

    #### ENCODAGE DES COUPS ############################################################################
    # 0000 0000 0000 0000 0011 1111   case de depart  0x3f
    # 0000 0000 0000 1111 1100 0000   case d'arrivee  0xfc0
    # 0000 0000 1111 0000 0000 0000   piece jouee  0xf000
    # 0000 1111 0000 0000 0000 0000   promotion  0xf0000
    # 0001 0000 0000 0000 0000 0000   capture flag  0x100000
    # 0010 0000 0000 0000 0000 0000   double push flag  0x200000
    # 0100 0000 0000 0000 0000 0000   en passant flag  0x300000
    # 1000 0000 0000 0000 0000 0000   castling flag  0x400000
    ####################################################################################################

    @staticmethod
    def encode_move(source,target,piece,promotion,capture,double,enpassant,castling):
        return source | (target << 6) | (piece << 12) | (promotion << 16) | (capture << 20) | (double << 21) | (enpassant << 22) | (castling << 23)
    @staticmethod
    def get_move_source(move):
        return move & 0x3f
    @staticmethod
    def get_move_target(move):
        return (move & 0xfc0) >> 6
    @staticmethod
    def get_move_piece(move):
        return (move & 0xf000) >> 12
    @staticmethod
    def get_move_promotion(move):
        return (move & 0xf0000) >> 16
    @staticmethod
    def get_move_capture(move):
        return (move & (1<<20)) != 0
    @staticmethod
    def get_move_double(move):
        return (move & (1<<21)) != 0
    @staticmethod
    def get_move_enpassant(move):
        return (move & (1<<22)) != 0
    @staticmethod
    def get_move_castling(move):
        return (move & (1<<23)) != 0


    def move_generation(self,side):
        """ génère les coups possibles du côté donné en argument """

        move_list = [] #liste des pseudo coups possibles encodé selon la forme d'au dessus

        # castling rights
        if side == WHITE:
            if self.castle_right & 1: # king castling
                if not (self.occupancies[2] & (2**F1 + 2**G1)):
                    print(self.occupancies[2] & (2**F1 + 2**G1))
                    if (not self.square_is_attacked(E1, BLACK)) and (not self.square_is_attacked(F1, BLACK)):
                        move_list.append(self.encode_move(E1, G1, K, NO_PIECE, 0, 0, 0, 1))
            if self.castle_right & 2: # queen castling
                if not (self.occupancies[2] & (2**D1 + 2**C1 + 2**B1)):
                    if (not self.square_is_attacked(E1, BLACK)) and (not self.square_is_attacked(D1, BLACK)):
                        move_list.append(self.encode_move(E1, C1, K, NO_PIECE, 0, 0, 0, 1))
        else:
            if self.castle_right & 4: # king castling
                if not (self.occupancies[2] & (2**F8 + 2**G8)):
                    if (not self.square_is_attacked(E8, WHITE)) and (not self.square_is_attacked(F8, WHITE)):
                        move_list.append(self.encode_move(E8, G8, k, NO_PIECE, 0, 0, 0, 1))
            if self.castle_right & 8: # queen castling
                if not (self.occupancies[2] & (2**D8 + 2**C8 + 2**B8)):
                    if (not self.square_is_attacked(E8, WHITE)) and (not self.square_is_attacked(D8, WHITE)):
                        move_list.append(self.encode_move(E8, C8, k, NO_PIECE, 0, 0, 0, 1))

        for piece in range(side*6,(side+1)*6): # on selectionne la bonne partie de bitboard en fonction du side
            bb = self.bitboard[piece]

            if piece == P : # pion blanc
                while bb:
                    depart = self.ls1b_index(bb)
                    bb = self.pop_bit(bb, depart) # on enlève la case de départ afin de regarder ensuite les suivantes

                    # attaque de pion
                    is_attacking = self.pawn_attack[0][depart] & self.occupancies[1]
                    while is_attacking:
                        arrivee = self.get_ls1b(is_attacking)
                        if arrivee <= H8: #on mange et on promotionne
                            move_list.append(self.encode_move(depart, arrivee, P, Q, 1, 0, 0, 0))
                            move_list.append(self.encode_move(depart, arrivee, P, R, 1, 0, 0, 0))
                            move_list.append(self.encode_move(depart, arrivee, P, B, 1, 0, 0, 0))
                            move_list.append(self.encode_move(depart, arrivee, P, N, 1, 0, 0, 0))
                        else:
                            move_list.append(self.encode_move(depart,arrivee,P,NO_PIECE,1,0,0,0))
                        is_attacking = self.pop_bit(is_attacking, arrivee)

                    # prise en passant
                    if self.en_passant != -1 and (self.pawn_attack[0][depart] & (1<<self.en_passant)):
                        move_list.append(self.encode_move(depart, self.en_passant, P, NO_PIECE, 1, 0, 1, 0))

                    # coup de pion blanc discret
                    arrivee = depart - 8
                    if arrivee>= A8 and not self.get_bit(self.occupancies[2],arrivee):

                        #promotion
                        if arrivee <= H8: #le pion arrive sur la dernière rangée
                            move_list.append(self.encode_move(depart,arrivee,P,Q,0,0,0,0))
                            move_list.append(self.encode_move(depart,arrivee,P,R,0,0,0,0))
                            move_list.append(self.encode_move(depart,arrivee,P,B,0,0,0,0))
                            move_list.append(self.encode_move(depart,arrivee,P,N,0,0,0,0))
                        else:
                            # avancée de 2 cases
                            if (A2 <= depart <= H2) and not self.get_bit(self.occupancies[2],arrivee-8):
                                move_list.append(self.encode_move(depart,arrivee-8,P,NO_PIECE,0,1,0,0))
                            move_list.append(self.encode_move(depart,arrivee,P,NO_PIECE,0,0,0,0))
            elif piece == p : # pion noir
                while bb:
                    depart = self.ls1b_index(bb)
                    bb = self.pop_bit(bb, depart) # on enlève la case de départ afin de regarder ensuite les suivantes

                    # attaque de pion
                    is_attacking = self.pawn_attack[1][depart] & self.occupancies[0]
                    while is_attacking:
                        arrivee = self.get_ls1b(is_attacking)
                        if arrivee >= A1: #on mange et on promotionne
                            move_list.append(self.encode_move(depart, arrivee, p, q, 1, 0, 0, 0))
                            move_list.append(self.encode_move(depart, arrivee, p, r, 1, 0, 0, 0))
                            move_list.append(self.encode_move(depart, arrivee, p, b, 1, 0, 0, 0))
                            move_list.append(self.encode_move(depart, arrivee, p, n, 1, 0, 0, 0))
                        else:
                            move_list.append(self.encode_move(depart, arrivee, p, NO_PIECE, 1, 0, 0, 0))

                        is_attacking = self.pop_bit(is_attacking, arrivee)
                    # prise en passant
                    if self.en_passant != -1 and (self.pawn_attack[1][depart] & (1<<self.en_passant)):
                        move_list.append(self.encode_move(depart, self.en_passant, p, NO_PIECE, 1, 0, 1, 0))

                    # coup de pion noir discret
                    arrivee = depart + 8 # + pour noir - pour blanc
                    if arrivee <= H1 and not self.get_bit(self.occupancies[2],arrivee):

                        #promotion
                        if arrivee >= A1: #le pion arrive sur la dernière rangée
                            move_list.append(self.encode_move(depart,arrivee,p,q,0,0,0,0))
                            move_list.append(self.encode_move(depart,arrivee,p,r,0,0,0,0))
                            move_list.append(self.encode_move(depart,arrivee,p,b,0,0,0,0))
                            move_list.append(self.encode_move(depart,arrivee,p,n,0,0,0,0))
                        else:
                            # avancée de 2 cases
                            if (A7 <= depart <= H7) and not self.get_bit(self.occupancies[2],arrivee+8):
                                move_list.append(self.encode_move(depart,arrivee+8,p,NO_PIECE,0,1,0,0))
                            move_list.append(self.encode_move(depart,arrivee,p,NO_PIECE,0,0,0,0))
            else: #autres pièces
                while bb:
                    depart = self.ls1b_index(bb)
                    bb = self.pop_bit(bb, depart) # on enlève la case de départ afin de regarder ensuite les suivantes
                    if piece in [K,k]:
                        attack_map = self.king_attack[depart] & ~(self.occupancies[side]) # on ne regarde pas les cases où il y a des pieces de la même couleur.
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
                        move_list.append(self.encode_move(depart, arrivee, piece, NO_PIECE, self.get_bit(self.occupancies[2], arrivee), 0, 0, 0))


        return move_list

    def print_move(self,side):
        liste = self.move_generation(side)
        print("\n")
        print("Coup   Piece  Capture  Double  Enpassant  Roque")
        print()
        for move in liste:
            coup = CASES[self.get_move_source(move)] + CASES[self.get_move_target(move)] + PIECE_LETTER[self.get_move_promotion(move)].lower()
            piece = PIECE_LETTER[self.get_move_piece(move)]
            capt = int(self.get_move_capture(move))
            double = int(self.get_move_double(move))
            enpass = int(self.get_move_enpassant(move))
            roque = int(self.get_move_castling(move))
            print("{0}  {1}      {2}        {3}       {4}          {5}".format(coup,piece,capt,double,enpass,roque))
        print("\nNombre de coup : %s"%len(liste))


        ############################################################################################################################################
        ##### // MAKE MOVE and UNDO MOVE FUNCTIONS // ##############################################################################################
        ############################################################################################################################################

    def undo_move(self, real_move):
        """ annule le dernier coup, si real_move = True alors on supprime d'abord la dernière entrée de l'historique sinon non """
        if real_move:
            del self.history[-1]
        (bb, occ, enpass, castle) = self.history[-1]
        self.bitboard = bb[:]
        self.occupancies = occ[:]
        self.en_passant = enpass
        self.castle_right = castle

    def make_move(self, move, only_capture_flag=False):
        """ fait le coup et l'ajoute à l'historique """

        if only_capture_flag:
            if self.get_move_capture(move):
                self.make_move(move,False)
            else:
                return 0 # on ne fait pas le coup
        else:
            # on récupère les informations du coup
            source = self.get_move_source(move)
            target = self.get_move_target(move)
            piece = self.get_move_piece(move)
            promote = self.get_move_promotion(move)
            capture = self.get_move_capture(move)
            double = self.get_move_double(move)
            enpass = self.get_move_enpassant(move)
            roque = self.get_move_castling(move)

            # on déplace la pièce
            self.bitboard[piece] = self.pop_bit(self.bitboard[piece], source)
            self.bitboard[piece] = self.set_bit(self.bitboard[piece], target)
            self.occupancies[self.side] = self.pop_bit(self.occupancies[self.side], source)
            self.occupancies[self.side] = self.set_bit(self.occupancies[self.side], target)
            self.occupancies[2] = self.pop_bit(self.occupancies[2], source) # quel que soit le coup il n'y aura plus de piece sur la case d'origine

            # on gère les captures
            if capture:
                self.occupancies[1-self.side] = self.pop_bit(self.occupancies[1-self.side], target) # on retire la piece de l'occupance global de la couleur attaquée

                for i in range((1-self.side)*6,(2-self.side)*6): # on parcours les pieces de la couleur adverse
                    if self.get_bit(self.bitboard[i], target):
                        self.occupancies[i] = self.pop_bit(self.occupancies[i], target)
                        break
            else:
                self.occupancies[2] = self.set_bit(self.occupancies[2], target) # il n'y avait pas de piece avant donc on doit l'ajouter
