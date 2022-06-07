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

occ = 0
occ = B.set_bit(occ)

B.print_bb(B.rook_mask[E4])
# B.print_board()
# mv_list = B.legal_move_generation(B.side)
# for mv in mv_list:
#     print(B.score_move(mv))
# print()
# mv_list = B.tri_move(mv_list)
# for mv in mv_list:
#     print(B.score_move(mv))
# print()
