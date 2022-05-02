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


B.set_fen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8")
# move,score = E.bot_move(4, B)
# depart = B.get_move_source(move)
# arrivee = B.get_move_target(move)
# print(CASES[depart],CASES[arrivee])

# occ = 0
# occ = B.set_bit(occ, D5)
# occ = B.set_bit(occ, D4)
# occ = B.set_bit(occ, E5)
# occ = B.set_bit(occ, E4)
#
#
# for case in range(64):
#     B.print_bb(B.get_bishop_attack(case, occ))
#     input()
