"""
Created on Sat May 28 17:09:03 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

MOVES
"""

# TODO : changer la représentation des coups

class Move:
    """ Représentation des coups """

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

    def __init__(self,source=0,target=0,piece=0,promotion=0,capture=0,double=0,enpassant=0,castling=0):
        pass
