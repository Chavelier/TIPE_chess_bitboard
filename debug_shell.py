# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:20:06 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

DEBUG SHELL
"""

from board import *
ascii_f = True
B = Board()


def clear():
    print(100*"\n")


cmd = ""

while cmd not in ["q","quit","exit"]:
    clear()
    print("Bienvenue dans le moteur d'echec de Corto et Hugo ! \n Tapez help pour les commandes... \n\n\n")
    if cmd == "help":
        print("redemarer une nouvelle partie -> restart")
        print("jouer un coup -> (case de depart)(case d'arrivee)(promotion) (ex : e2e4 ou c2c1q)")
        print("annuler un coup -> undo")
        print("activer/desactiver l'affichage ASCII -> ascii")
        print("afficher la liste des coups jouables -> moves")
        print("charger un fen -> set fen rnbqkbnr/ppp2ppp/4p3/3p4/Q1PP4/8/PP2PPPP/RNB1KBNR b KQkq - 1 3 (ex)")
    elif cmd == "restart":
        B.init()
    elif cmd == "ascii":
        ascii_f = not ascii_f
    elif cmd == "moves":
        B.print_move(B.side)
    elif "set fen" in cmd:
        B.set_fen(cmd.split()[2:])
    elif cmd == "undo":
        B.undo_move(True)
    elif 4 <= len(cmd) <= 5:
        coup = cmd
        if len(cmd) == 4:
            coup += " "
        mv = B.trad_move(coup)
        if mv != -1:
            B.make_move(mv)
        
        
    B.print_board(ascii_f)
    cmd = input("\n>>> ")
