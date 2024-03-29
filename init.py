""" INIT """

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
FILE = [72340172838076673,
144680345676153346,
289360691352306692,
578721382704613384,
1157442765409226768,
2314885530818453536,
4629771061636907072,
9259542123273814144]

NOT_A_FILE = ~FILE[0]
NOT_H_FILE = ~FILE[7]
NOT_AB_FILE = ~(FILE[0] | FILE[1])
NOT_GH_FILE = ~(FILE[6] | FILE[7])

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

[P,N,B,R,Q,K,p,n,b,r,q,k] = range(12)
NO_PIECE = 12 # utile pour l'encodage des coups
PIECE_LETTER = "PNBRQKpnbrqk "
PIECE_ASCII = { p : "♙", k : "♔", q : "♕", n : "♘", b : "♗", r : "♖",
                   P : "♟︎", K : "♚", Q : "♛", N : "♞", B : "♝", R : "♜"}
PIECE_LETTER_IMAGES = ["p_00",'p_01','p_02','p_03','p_04','p_05','p_06','p_07','p_08','p_09','p_10','p_11']
PIECE_VAL = [100,300,300,500,900,0,-100,-300,-300,-500,-900,0]

PAWN_POS_SCORE = [
    90,  90,  90,  90,  90,  90,  90,  90,
    30,  30,  30,  30,  30,  30,  30,  30,
    15,  15,  20,  20,  20,  20,  15,  15,
     8,   8,   8,  25,  25,   8,   8,   8,
     5,   5,  10,  20,  20,   5,   5,   5,
     0,   0,   0,   5,   5,   0,   0,   0,
     8,   8,   8, -30, -30,  10,  10,  10,
     0,   0,   0,   0,   0,   0,   0,   0 ]
KNIGHT_POS_SCORE = [
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   5,   5,   0,   0,  -5,
    -5,   5,  10,  10,  10,  10,   5,  -5,
    -5,   5,  10,  15,  15,  10,   5,  -5,
    -5,   5,  10,  15,  15,  10,   5,  -5,
    -5,   5,  10,   5,   5,  10,   5,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5, -30,   0,   0,   0,   0, -30,  -5 ]
BISHOP_POS_SCORE = [
     0,   0,   0,   0,   0,   0,   0,   0,
     0,   0,   0,   0,   0,   0,   0,   0,
     0,   0,   0,   8,   8,   0,   0,   0,
     0,  10,   8,   4,   4,   8,  10,   0,
     0,   0,  10,   4,   4,  10,   0,   0,
     0,   5,   0,   0,   0,   0,   5,   0,
     0,  20,   0,   5,   5,   0,  20,   0,
     0,   0, -30,   0,   0, -30,   0,   0 ]
ROOK_POS_SCORE = [
    50,  50,  50,  50,  50,  50,  50,  50,
    50,  50,  50,  50,  50,  50,  50,  50,
     0,   0,  10,  20,  20,  10,   0,   0,
     0,   0,  10,  20,  20,  10,   0,   0,
     0,   0,  10,  20,  20,  10,   0,   0,
     0,   0,  10,  20,  20,  10,   0,   0,
     0,   0,  10,  20,  20,  10,   0,   0,
     0,   0,  10,  20,  20, 10,   0,   0 ]
QUEEN_POS_SCORE = [
     0,   0,   0,   0,   0,   0,   0,   0,
     0,   0,   2,   2,   2,   2,   0,   0,
     0,   2,   2,   5,   5,   2,   2,   0,
     0,   2,   5,  10,  10,   5,   2,   0,
     0,   2,   5,  10,  10,   5,   2,   0,
     0,   0,   2,   2,   2,   2,   0,   0,
     0,   2,   2,   2,   2,   2,   2,   0,
     0,   0,   0,   5,   0,   0,   0,   0  ]
KING_POS_SCORE = [
     0,   0,   0,   0,   0,   0,   0,   0,
     0,   0,   5,   5,   5,   5,   0,   0,
     0,   5,   5,  10,  10,   5,   5,   0,
     0,   5,  10,  20,  20,  10,   5,   0,
     0,   5,  10,  20,  20,  10,   5,   0,
     0,   0,   5,  10,  10,   5,   0,   0,
     0,   5,   5,  -5,  -5,   0,   5,   0,
     10, 35,  10,  -5,  -2,   0,  40,  10  ]
POS_SCORE = [PAWN_POS_SCORE,KNIGHT_POS_SCORE,BISHOP_POS_SCORE,ROOK_POS_SCORE,QUEEN_POS_SCORE,KING_POS_SCORE]
MIRROR_CASE = [
	A1, B1, C1, D1, E1, F1, G1, H1,
	A2, B2, C2, D2, E2, F2, G2, H2,
	A3, B3, C3, D3, E3, F3, G3, H3,
	A4, B4, C4, D4, E4, F4, G4, H4,
	A5, B5, C5, D5, E5, F5, G5, H5,
	A6, B6, C6, D6, E6, F6, G6, H6,
	A7, B7, C7, D7, E7, F7, G7, H7,
	A8, B8, C8, D8, E8, F8, G8, H8 ]



"""
   (Victims) Pawn Knight Bishop   Rook  Queen   King
 (Attackers)
       Pawn   105    205    305    405    505    605
     Knight   104    204    304    404    504    604
     Bishop   103    203    303    403    503    603
       Rook   102    202    302    402    502    602
      Queen   101    201    301    401    501    601
       King   100    200    300    400    500    600
      """

MVV_LVA = [ # matrice pour classer les captures en fonction de leur ordre d'importance ([attaquant][victime])
[105,205,305,405,505,605,105,205,305,405,505,605],
[104,204,304,404,504,604,104,204,304,404,504,604],
[103,203,303,403,503,603,103,203,303,403,503,603],
[102,202,302,402,502,602,102,202,302,402,502,602],
[101,201,301,401,501,601,101,201,301,401,501,601],
[100,200,300,400,500,600,100,200,300,400,500,600],
[105,205,305,405,505,605,105,205,305,405,505,605],
[104,204,304,404,504,604,104,204,304,404,504,604],
[103,203,303,403,503,603,103,203,303,403,503,603],
[102,202,302,402,502,602,102,202,302,402,502,602],
[101,201,301,401,501,601,101,201,301,401,501,601],
[100,200,300,400,500,600,100,200,300,400,500,600]]



EMPTY_POS = "8/8/8/8/8/8/8/8 b - - "
START_POS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 "
TRICKY_POS = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1 "
KILLER_POS = "rnbqkb1r/pp1p1pPp/8/2p1pP2/1P1P4/3P3P/P1P1P3/RNBQKBNR w KQkq e6 0 1"
CMK_POS = "r2q1rk1/ppp2ppp/2n1bn2/2b1p3/3pP3/3P1NPP/PPP1NPB1/R1BQ1RK1 b - - 0 9 "
REPETITION_POS = "2r3k1/R7/8/1R6/8/8/P4KPP/8 w - - 0 40 "

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
