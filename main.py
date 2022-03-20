# -*- coding: utf-8 -*-
"""
Created on Mon Feb  21 12:38:25 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

MAIN
"""
from board import *

B = Board()
# B.print_board()
# B.set_fen('r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 5 4')
# B.print_board()
# B.print_move(WHITE)

# move = B.encode_move(E4, D5, P, NO_PIECE, True, False, False, False)
# print(B.get_move_source(move))
# print(B.get_move_target(move))
# print(B.get_move_piece(move))
# print(B.get_move_promotion(move))
# print(B.get_move_capture(move))
# print(B.get_move_double(move))
# print(B.get_move_enpassant(move))
# print(B.get_move_castling(move))

# a = ""
# while a != "q":
#     a = input(">>> ")

# move_list = B.move_generation(WHITE)
# for mv in move_list:
#     B.make_move(mv,False)
#     B.print_board()
#     B.is_occupancies_correct()
#     B.undo_move(False)
#     input("...")


B.perft_test(4)
