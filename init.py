# -*- coding: utf-8 -*-
"""
Created on Mon Feb  21 12:33:24 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

INIT
"""


"""
bitboard echequier representation :

8   0  1  2  3  4  5  6  7
7   8  9  10 11 12 13 14 15
6   16 17 18 19 20 21 22 23
5   24 25 26 27 28 29 30 31
4   32 33 34 35 36 37 38 39
3   40 41 42 43 44 45 46 47
2   48 49 50 51 52 53 54 55
1   56 57 58 59 60 61 62 63

    A  B  C  D  E  F  G  H

ex: case E4 a comme id 36 et comme représentation en bitboard 2**36
"""

import random as rd

### DECLARATION DES CONSTANTES

CASES = [
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"
    ]

[   A8, B8, C8, D8, E8, F8, G8, H8,
    A7, B7, C7, D7, E7, F7, G7, H7,
    A6, B6, C6, D6, E6, F6, G6, H6,
    A5, B5, C5, D5, E5, F5, G5, H5,
    A4, B4, C4, D4, E4, F4, G4, H4,
    A3, B3, C3, D3, E3, F3, G3, H3,
    A2, B2, C2, D2, E2, F2, G2, H2,
    A1, B1, C1, D1, E1, F1, G1, H1  ] = range(64)

#bitboard constantes
ALL = 2**64-1
EMPTY = 0
A_FILE = 72340172838076673
B_FILE = 144680345676153346
G_FILE = 4629771061636907072
H_FILE = 9259542123273814144
NOT_A_FILE = ~A_FILE
NOT_H_FILE = ~H_FILE
NOT_AB_FILE = ~(A_FILE | B_FILE)
NOT_GH_FILE = ~(G_FILE | H_FILE)

[WHITE,BLACK] = [0,1]

BISHOP_RELEVANT_BITS = [
    6, 5, 5, 5, 5, 5, 5, 6,
    5, 5, 5, 5, 5, 5, 5, 5,
    5, 5, 7, 7, 7, 7, 5, 5,
    5, 5, 7, 9, 9, 7, 5, 5,
    5, 5, 7, 9, 9, 7, 5, 5,
    5, 5, 7, 7, 7, 7, 5, 5,
    5, 5, 5, 5, 5, 5, 5, 5,
    6, 5, 5, 5, 5, 5, 5, 6
]
ROOK_RELEVANT_BITS = [
    12, 11, 11, 11, 11, 11, 11, 12,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    12, 11, 11, 11, 11, 11, 11, 12
]

[P,K,Q,B,N,R,p,k,q,b,n,r] = range(12)
NO_PIECE = 12 # utile pour l'encodage des coups
PIECE_LETTER = "PKQBNRpkqbnr "
PIECE_LETTER_IMAGES = ["wp",'wK','wQ','wB','wN','wR','bp','bK','bQ','bB','bN','bR']
PIECE_LETTER.index('P')
PIECE_ASCII = { p : "♙", k : "♔", q : "♕", n : "♘", b : "♗", r : "♖",
                   P : "♟︎", K : "♚", Q : "♛", N : "♞", B : "♝", R : "♜"}



# génération aléatoire d'un nombre pour le magic number ################################

# random_state = 1804289383 # seed de départ
#
# def get_32b_random_nb():
#     global random_state
#     nb = random_state
#
#     nb = nb ^ (nb << 13)
#     nb = nb ^ (nb >> 17)
#     nb = nb ^ (nb << 5)
#
#     random_state = nb
#     return nb
#
# def get_64b_random_nb():
#
#     #on initialise des nombres
#     n1 = get_32b_random_nb() & (2**16-1)
#     n2 = get_32b_random_nb() & (2**16-1)
#     n3 = get_32b_random_nb() & (2**16-1)
#     n4 = get_32b_random_nb() & (2**16-1)
#
#     #renvoi nombre aleatoire
#     return n1 | (n2 << 16) | (n3 << 32) | (n4 << 48)

def generate_magic_number(): #genere un magic number candidat
    # get_64b_random_nb() & get_64b_random_nb() & get_64b_random_nb()
    return rd.randint(0,ALL) & rd.randint(0,ALL) & rd.randint(0,ALL)
