# -*- coding: utf-8 -*-
"""
Created on Tue Mar  8 14:20:06 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

DEBUG SHELL
"""

from engine import *
import time
import pyperclip

ascii_f = False
board = Board()
E = Engine()



def clear():
    print(100*"\n")


cmd = ""

while cmd not in ["q","quit","exit"]:
    clear()
    print("Bienvenue dans le moteur d'echec de Corto et Hugo ! \n Tapez help pour les commandes... \n\n\n")
    if cmd == "help":
        print("redemarer une nouvelle partie -> restart")
        print("jouer un coup -> [depart][arrivee][promotion] (ex : e2e4 ou c2c1q)")
        print("annuler un coup -> undo")
        print("jouer un coup d'ordinateur à la profondeur x -> go [x]")
        print("activer/desactiver l'affichage ASCII -> ascii")
        print("afficher la liste des coups jouables -> moves")
        print("charger un fen -> fen rnbqkbnr/ppp2ppp/4p3/3p4/Q1PP4/8/PP2PPPP/RNB1KBNR b KQkq - 1 3 (ex)")
        print("copier le fen -> cfen")
        print("tester les performances à la profondeur x -> perf [x]")
    elif cmd == "restart":
        board.init()
    elif cmd == "debug":
        board.add_to_history()
    elif cmd == "ascii":
        ascii_f = not ascii_f
    elif "go" in cmd:
        if cmd == "go":
            depth = 4
        else:
            depth = int(cmd.split()[1])
        tic = time.time()
        mv,score,nodes,max_depth = E.bot_move(depth, board)
        # coup = CASES[B.get_move_source(mv)]+CASES[B.get_move_target(mv)]
        # piece = PIECE_LETTER[B.get_move_piece(mv)]
        # print("piece : {} \nmeilleur coup : {} \nscore : {}".format(piece,coup, score))
        print("Score calculé : %s"%score)
        print("Noeuds visités : %s"%nodes)
        print("Profondeur maximale atteinte : %s"%max_depth)
        board.make_move(mv)
        print("Temps de calcul : %ss"%(time.time()-tic))
        print("\ncoup joué : %s"%(PIECE_LETTER[board.get_move_piece(mv)]+" "+CASES[board.get_move_source(mv)]+CASES[board.get_move_target(mv)]))
    elif cmd == "moves":
        board.print_move(board.side)
    elif cmd == "cfen":
        pyperclip.copy(board.get_fen())
    elif  cmd[0:4] == "fen ":
        fen = str(cmd[4:])
        print(fen)
        board.set_fen(fen)
    elif "perf" in cmd:
        depth = int(cmd.split()[1])
        board.perft_test(depth)
    elif cmd == "undo":
        board.undo_move(True)
    elif 4 <= len(cmd) <= 5:
        coup = cmd
        if len(cmd) == 4:
            coup += " "
        mv = board.trad_move(coup)
        if mv != -1:
            print(board.score_move(mv))
            board.make_move(mv)


    board.print_board(ascii_f)
    cmd = input("\n>>> ")
