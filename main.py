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

mv_list = B.legal_move_generation(B.side)
mv_list2 = B.legal_move_generation(B.side)

for i in range(len(mv_list)):
    print(mv_list[i]==mv_list2[i])

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
