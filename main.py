# -*- coding: utf-8 -*-
"""
Created on Mon Feb  21 12:38:25 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

MAIN
"""
from board import *
from engine import *

B = Board()
E = Engine()

occ = B.set_bit(0, C4)
occ = B.set_bit(occ,F6)
B.print_bb(occ)
B.print_bb(B.get_rook_attack(E4, occ))

# B.set_fen(TRICKY_POS)
# B.print_board()
# mv_list = B.legal_move_generation(B.side)
# for mv in mv_list:
#     print(B.score_move(mv))
# print()
# mv_list = B.tri_move(mv_list)
# for mv in mv_list:
#     print(B.score_move(mv))
# print()
