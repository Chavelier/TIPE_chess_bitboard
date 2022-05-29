# -*- coding: utf-8 -*-

#TODO BUG CLICK TROP LONG QUI VIENT DE LAJOUT DU BOUTON MENU (DEPLACER LE TRUC?)
"""
Created on Tue Mar  8 14:20:06 2022

@author: Corto Cristofoli
@co-author : Jeunier Hugo
@secret-author : Lance-Perlick Come

INTERFACE GRAPHIQUE
"""

import pygame as py
import board
import time
import sys
import math
import pyperclip
import openfinals
from init import *
from pygamebutton import Button

vert_sapin,bleuPSV,brown,white_brown,almost_white,blue,green_chess_com = (30,79,27),(17,141,129),(184,140,100),(248,220,180),(235,236,208),(64,112,162),(119,149,86)
colors = [almost_white,green_chess_com]

py.init()
icone = py.image.load("assets/chessico.png")
py.display.set_icon(icone)
py.display.set_caption("Chess Engine")
clock = py.time.Clock()
sounds = [py.mixer.Sound('assets/sounds/start.mp3'),py.mixer.Sound('assets/sounds/move.mp3'),
            py.mixer.Sound('assets/sounds/take.mp3'),py.mixer.Sound('assets/sounds/castling0.mp3'),
            py.mixer.Sound('assets/sounds/check0.mp3')]
WIDTH,HEIGHT,DIMENSION = 512,512,8 #Dimension de l'échiquier
SQ_SIZE = HEIGHT // DIMENSION #Taille des cases

RED_CASE_CHECK = py.Surface((SQ_SIZE,SQ_SIZE))
RED_CASE_CHECK.set_alpha(60)
RED_CASE_CHECK.fill(py.Color('red'))

BAR_WIDTH = 0
MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT,MAX_FPS,IMAGES = int(HEIGHT/3),HEIGHT,60,{} #GERE LE TICK POUR LES ANIMS ETC, SI ON A BESOIN DE RAM ON LE PASSE A TRES PEU
FINAL_WIDTH = WIDTH + MOVE_LOG_PANEL_WIDTH
colsToFiles = {0:"a", 1:"b", 2:"c", 3:"d", 4:"e", 5:"f", 6:"g", 7:"h"}
filesToCols = {v : k for k,v in colsToFiles.items()}
current_evaluation = 0

screen = py.display.set_mode((FINAL_WIDTH,HEIGHT))
BACKGROUND = py.transform.scale(py.image.load("assets/background.jpg"), (FINAL_WIDTH, HEIGHT))

"""FONCTIONS AUXILIAIRES"""
def loadImages():
    """ Initialise un dictionnaire global pour les images (une seule fois avec pygame sinon trop lourd)"""

    for piece in PIECE_LETTER[:-1]:
        IMAGES[piece] = py.image.load("assets/" + PIECE_LETTER_IMAGES[PIECE_LETTER.index(piece)] + ".png")

def activation_function(x):
    """Prend en entrée la valeur de l'évaluation actuelle de la position et renvoie la longueur
    de la partie noire de la barre"""

    phi = (1+math.sqrt(5))/2
    alpha = math.sqrt(5)*phi
    return (2/(1+math.exp(-x/(alpha))))-1

def liste_to_move(l):
    """Prend en entrée une liste représentant les deux couples case arrivée/case départ
    et renvoie la traduction du coup. Ex : [(0,0),(7,7)] devient 'a8h1'"""
    s = ''
    for (row,col) in l:
        s += CASES[8*row+col]
    return s


"""FONCTIONS D'AFFICHAGE"""
def run(eval_bar_flag,nbjoueur,pgn_game,fen_board,depth=4,PGN=False,FEN=False,history=[]):
    """Tourne en boucle et actualise le board en fonction des entrées de l'utilisateur"""

    B = board.Board()
    side = WHITE
    if FEN:
        B.set_fen(fen_board)
        side = B.side
    py.init()
    screen.fill(py.Color("black"))
    valid_moves,move_made,animate,running,game_over = B.legal_move_generation(side),False,False,True,False  #TODO Servira pour jouer uniquement des coups valides!#Flag utilisé lorsqu'un move est joué (est utile pour éviter les bugs),#flag pour savoir si on doit animer,#A voir quand il y aura les mats !! #TODO ce n'est pas pour tout de suite
    loadImages() #On fait ça une seule fois avant la boucle while
    sounds[0].play()
    sq_selected,player_clicks,pgn_history = (),[],history #Pas de case sélectionnée initialement, tuple(row,col) #Garder la trace des cliques de l'utilisateur (deux tuples(row,col))
    moveLogFont,coordFont = py.font.SysFont("Montserrat",20,False,False),py.font.SysFont("Montserrat",18,False,False)


    def play_sound(mv):
        if B.get_move_capture(mv):
            sounds[2].play()
        elif B.get_move_castling(mv):
            sounds[3].play()
        elif B.square_is_attacked(B.ls1b_index(B.bitboard[K+B.side*6]),1-B.side):
            sounds[4].play()
        else:
            sounds[1].play()

    while running:
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False
            #Gestionnaire de la souris:
            elif e.type == py.MOUSEBUTTONDOWN: #Drag and drop peut-être après
                if not game_over:
                    location = py.mouse.get_pos() #(x,y) coordonnées de la souris
                    col,row = location[0]//SQ_SIZE,location[1]//SQ_SIZE
                    case,occ_case = 8*row+col,False #occ_case prend la valeur true si la case est occupée
                    for i in range(12):
                        if B.get_bit(B.bitboard[i],case):
                            occ_case=True
                    if sq_selected == (row,col) or col >= 8 or (len(player_clicks) == 0 and not(occ_case)): #L'utilisateur a cliqué sur la même cases ou a cliqué à côté
                        sq_selected,player_clicks = (),[]
                    else:
                        sq_selected = (row,col)
                        player_clicks.append(sq_selected) #On append de la même manière pour le premier et deuxième clic
                    if len(player_clicks) == 2: #Après le 2nd click
                        coup = liste_to_move(player_clicks)
                        if len(coup) == 4:
                            coup += " "
                        mv = B.trad_move(coup)
                        if mv != -1:
                            val_move = B.make_move(mv)
                            print(openfinals.find_book_moves(B.get_fen()))
                            #print(openfinals.find_endgame_pos_val(None))
                            if val_move == 1:
                                move_made,animate = True,True
                                play_sound(mv)
                                sq_selected,player_clicks = (),[] #On reste les clicks
                                pgn_history.append(B.move_to_pgn(mv,valid_moves))
                        else:
                            player_clicks = [sq_selected] #Petit tips : quand le deuxième clic d'une première pièce n'est pas sur une case autorisée par un coup légal, la case du deuxième du clic devient la case de départ !!
                            animate = False

            #Gestionnaire du clavier
            elif e.type == py.KEYDOWN:
                if e.key == py.K_z: #undo depuis la touche Z (peut être changé)
                    B.undo_move(True)
                    if pgn_history != []:
                        pgn_history = pgn_history[:-1]
                    move_made,animate = True,False
                    valid_moves = B.legal_move_generation(B.side)
                if e.key == py.K_r: #Rester le board avec la touche 'r'
                    B.init()
                    valid_moves,sq_selected,player_clicks,pgn_history = B.legal_move_generation(WHITE),(),[],[]
                    move_made,animate = False,False

        if move_made:
            if animate:
                animate_move(mv,screen,B,clock,coordFont)
                valid_moves,move_made,animate = B.legal_move_generation(B.side),False,False
        draw_game_state(screen,B,valid_moves,sq_selected,moveLogFont,coordFont,pgn_history,[eval_bar_flag] + [round(B.evaluation()/100,1)]) #TODO board.eval
        draw_menu_buttons(screen,eval_bar_flag,depth,B,history)
        clock.tick(MAX_FPS)
        py.display.flip()


def highlight_squares(screen,B,valid_moves,sq_selected):
    """Surligne les cases légales pour une pièce sélectionnée
    Surligne aussi la case d'arrivée et de départ du dernier coup"""

    colors_soft = [soft_green,soft_white] = [(106,135,77),(214,214,189)]
    row,col = sq_selected
    s = py.Surface((SQ_SIZE,SQ_SIZE))
    s.set_alpha(90)
    s.fill(py.Color('yellow'))

    case,occ_case = 8*row+col,False #occ_case prend la valeur true si la case d'arrivée est occupée
    for i in range(12):
        if B.get_bit(B.bitboard[i],case):
            occ_case=True
    if occ_case: #TODO test case vide
        screen.blit(s,(col*SQ_SIZE,row*SQ_SIZE))

    #On surligne sur les cases légales pour la pièce
    for move in valid_moves:
        case_depart = B.get_move_source(move)
        case_arrivee = B.get_move_target(move)
        start_row,start_col = case_depart//8,case_depart%8
        end_row,end_col = case_arrivee//8,case_arrivee%8
        if start_row == row and start_col == col:
            color = colors_soft[((end_row+end_col)%2)-1]
            py.draw.circle(screen,color,(64*end_col+32,64*end_row +32),12,12)


def draw_board(screen,font):
    """Dessine l'échiquier (dont les numéros des cases)"""

    #colors = [p.Color("White"),vertSapin]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color,case = colors[((r+c)%2)],py.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE) #Petite astuce mathématique !
            py.draw.rect(screen,color,case)
            if r == 7:
                text = colsToFiles[c]
                text_object,text_location = font.render(text,True,colors[((r+c)%2)-1]),case.move(SQ_SIZE-10,SQ_SIZE-13) #Comme ca ca décale
                screen.blit(text_object,text_location)
            if c == 0:
                text = str(DIMENSION-r)
                text_object,text_location = font.render(text,True,colors[((r+c)%2)-1]),case.move(3,2) #Comme ca ca décale
                screen.blit(text_object,text_location)


def draw_pieces(screen,B):
    """Dessine les pièces"""

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece,case,occ_case = '',8*r+c,False #occ_case prend la valeur true si la case est occupée
            for i in range(12):
                if B.get_bit(B.bitboard[i],case):
                    occ_case,piece=True,PIECE_LETTER[i]
            if occ_case: #SI LENDROIT OU ON LA POSE EST DIFFERENT DE VIDE
                screen.blit(IMAGES[piece],py.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE))


def animate_move(move,screen,B,clock,font): #C'est pas le plus opti mais oklm ça fonctionne que 1s
    """Anime l'échiquier et déplace la pièce"""

    start_case,end_case = CASES[B.get_move_source(move)],CASES[B.get_move_target(move)]
    start_col,end_col = filesToCols[start_case[0]],filesToCols[end_case[0]]
    start_row,end_row = 8-int(start_case[1]),8-int(end_case[1])
    dR,dC = end_row-start_row,end_col-start_col

    frames_per_square = 10 #nombre de frame pour le move
    frame_count = (abs(dR) + abs(dC)) * frames_per_square

    for frame in range(frame_count + 1):
        row,col = (start_row + dR*frame/frame_count,start_col + dC*frame/frame_count)
        draw_board(screen,font)
        draw_pieces(screen,B)
        color,end_square = colors[(end_row + end_col)%2],py.Rect(end_col*SQ_SIZE,end_row*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        py.draw.rect(screen,color,end_square)
        case,occ_case = 8*end_row+end_col,False #occ_case prend la valeur true si la case d'arrivée est occupée
        for i in range(12):
            if B.get_bit(B.bitboard[i],case):
                occ_case=True
        #if occ_case:
            #screen.blit(IMAGES[piecearrivee], end_square) TODO
        screen.blit(IMAGES[PIECE_LETTER[B.get_move_piece(move)]], py.Rect(col*SQ_SIZE,row*SQ_SIZE, SQ_SIZE,SQ_SIZE))
        py.display.flip()
        clock.tick(480)


def draw_game_state(screen,B,valid_moves,sq_selected,moveLogFont,coordFont,pgn_history,bar):
    """Trace le board et les pièces en fonction de l'état du jeu"""

    if bar[0]:
        draw_bar(screen,bar[1],coordFont)
    draw_board(screen,coordFont)
    if sq_selected != ():
        highlight_squares(screen,B,valid_moves,sq_selected)
    case = B.ls1b_index(B.bitboard[K+B.side*6])
    if B.square_is_attacked(case,1-B.side):
        row,col = case//8,case%8
        screen.blit(RED_CASE_CHECK,(col*SQ_SIZE,row*SQ_SIZE))
    draw_pieces(screen,B)
    draw_move_log(screen,moveLogFont,pgn_history,bar[0])
    #draw_move_log(screen,moveLogFont,[CASES[i%64] for i in range(200)],bar[0])



def draw_bar(screen,val,font):
    """Si la barre d'évalution est activée, cette fonction la dessine en prenant en compte
    l'évaluation actuelle de la position"""


    black_height = (1-activation_function(val))*(HEIGHT//2)
    white_bar_rect = py.Rect(WIDTH,black_height,30,HEIGHT-black_height)
    py.draw.rect(screen,py.Color('white'),white_bar_rect)
    black_bar_rect = py.Rect(WIDTH,0,30,black_height)
    py.draw.rect(screen,py.Color('black'),black_bar_rect)

    if val > 0:
        screen.blit(font.render(str(val),True,py.Color('black')),(WIDTH+5,HEIGHT-20))
    else:
        screen.blit(font.render(str(abs(val)),True,py.Color('white')),(WIDTH+5,5))


def draw_move_log(screen,font,history,bar_flag):
    """Dessine un rectangle sur le côté où se trouvent les coups en format PGN"""

    ajout_dim = 0
    if bar_flag:
        ajout_dim = 30
    n = len(history)

    move_log_rect,move_texts,count_move = py.Rect(WIDTH + ajout_dim,0,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT-30),[],1 #Début,début,taille, taille
    py.draw.rect(screen,(28,28,28),move_log_rect)
    for j in range(0,n): #Pour avoir 1. e4 e5 2. Nc3 Nf6
        if j%2 == 0:
            move_string = ' ' + str(count_move) + '. ' + history[j] + ' '
            count_move += 1
        else:
            move_string = history[j]
        move_texts.append(move_string)
    if count_move >= 31:
        if n%2 != 0:
            n += 1
        move_texts = move_texts[n-count_move + count_move%2 - 20:]
    moves_per_row,padding,line_spacing = 2,5,2 #Choix arbitraire de mettre un nb de moves sur les lignes
    textY = padding
    for i in range(0,len(move_texts),moves_per_row):
        text = " "
        for k in range(moves_per_row):
            if i+k < len(move_texts):
                text += move_texts[i+k] + " "
        text_object,text_location = font.render(text,True,py.Color('white')),move_log_rect.move(padding,textY)#Comme ca ca décale
        screen.blit(text_object,text_location)
        textY += text_object.get_height() + line_spacing


def draw_menu_buttons(screen,bar_flag,depth,B,history):
    """ Dessine une barre de menu en dessous du rectangle de l'historique"""

    ajout_dim = 0
    if bar_flag:
        ajout_dim = 30

    parametre_button = Button(image=py.image.load("assets/setting_button.png"), pos=(WIDTH + MOVE_LOG_PANEL_WIDTH - 20,HEIGHT -20),
                                    text_input="", font=py.font.Font("assets/vcr.ttf", 20), base_color="#d4e6fc", hovering_color="White")
    location = py.mouse.get_pos()
    parametre_button.changeColor(location)
    parametre_button.update(screen)
    rect = py.Rect(WIDTH + ajout_dim,MOVE_LOG_PANEL_HEIGHT-30,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT)#Début,début,taille, taille
    py.draw.rect(screen,(28,28,28),rect)

    if parametre_button.checkForInput(location):
        for e in py.event.get():
            if e.type == py.MOUSEBUTTONDOWN:
                options_in_game(bar_flag,depth,B,history)
    parametre_button.changeColor(location)
    parametre_button.update(screen)

def pgn_or_fen():
    """Lancer une position FEN ou une partie PGN"""

    flag = True
    largeur = FINAL_WIDTH
    hauteur = HEIGHT
    PGN,FEN,CTRLV = False,False,''
    typeN = 0
    type = ['PGN','FEN']
    texts_button = ['Cliquer ici',type[typeN],'Valider']


    def get_font(size):
        #return py.font.SysFont("Montserrat",size,False,False)
        return py.font.Font("assets/vcr.ttf", size)

    while flag:
        screen.blit(BACKGROUND, (0, 0))
        MENU_MOUSE_POS = py.mouse.get_pos()

        button_list = []

        for i in range(3):
            button_list.append(Button(image=py.image.load("assets/midrect.png"), pos=(largeur//2 + 10, 150 + 100*i),
                                text_input=texts_button[i], font=get_font(35), base_color="#d4e6fc", hovering_color="White"))

        for button in button_list:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                sys.exit()
            if event.type == py.MOUSEBUTTONDOWN:
                if button_list[0].checkForInput(MENU_MOUSE_POS):
                    CTRLV = pyperclip.paste()
                    texts_button[0] = 'Lien collé'
                if button_list[1].checkForInput(MENU_MOUSE_POS):
                    typeN = 1-typeN
                    texts_button[1] = type[typeN]
                if button_list[2].checkForInput(MENU_MOUSE_POS):
                    if typeN:
                        return False,True,CTRLV
                    else:
                        return True,False,CTRLV

        py.display.update()

def options_in_game(eval_bar_flag0,depth0,B,pgn_history):
    """Menu des options
    Liste des options en cours de jeu:
                        - Profondeur : [|1:10|] sous forme de curseur sur une barre
                        - Barre d'éval ou non : Oui / Non
                        - Sauvegarder PGN/FEN
                        - Retour"""

    flag = True
    largeur = FINAL_WIDTH
    hauteur = HEIGHT
    eval_bar_flag = eval_bar_flag0
    depth = depth0


    def get_font(size):
        return py.font.Font("assets/vcr.ttf", size)

    while flag:
        screen.blit(BACKGROUND, (0, 0))
        MENU_MOUSE_POS = py.mouse.get_pos()
        button_list = []
        texts_button_list = ["IA depth: " + str(depth),"Eval: " + str(eval_bar_flag),
                            "Save FEN","Save PGN","Retour"]

        for i in range(len(texts_button_list)):
            button_list.append(Button(image=py.image.load("assets/midrect.png"), pos=(largeur//2 + 10, 50 + 100*i),
                                text_input=texts_button_list[i], font=get_font(35), base_color="#d4e6fc", hovering_color="White"))


        for button in button_list:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                sys.exit()
            if event.type == py.MOUSEBUTTONDOWN:
                if button_list[0].checkForInput(MENU_MOUSE_POS):
                    depth = 1+(depth%7)
                if button_list[1].checkForInput(MENU_MOUSE_POS):
                    eval_bar_flag = not(eval_bar_flag)
                if button_list[2].checkForInput(MENU_MOUSE_POS):
                    pyperclip.copy(B.get_fen())
                    print("FEN copié")
                if button_list[3].checkForInput(MENU_MOUSE_POS):
                    count_move = 1
                    txt = ''
                    for i in range(len(pgn_history)):
                        if i%2 == 0:
                            txt += ' ' + str(count_move) + '. ' + pgn_history[i] + ' '
                            count_move += 1
                        else:
                            txt += pgn_history[i]
                    pyperclip.copy(txt[1:-1])
                    print("PGN copié")
                if button_list[4].checkForInput(MENU_MOUSE_POS):
                    CTRLV = B.get_fen()
                    flag = False
                    run(eval_bar_flag,1,CTRLV,CTRLV,depth,FEN=True,history=pgn_history)

        py.display.update()

def options(eval_bar_flag0,nbjoueurs0,depth0):
    """Menu des options
    Liste des options : - Jeu à deux ou contre l'ordi : 1 joueur / 2 joueurs
                        - Profondeur : [|1:10|] sous forme de curseur sur une barre
                        - Partie depuis fenboard : [case pour mettre la fenboard] / bouton charger
                        - Barre d'éval ou non : Oui / Non
                        - Retour"""

    flag = True
    largeur = FINAL_WIDTH
    hauteur = HEIGHT
    eval_bar_flag = eval_bar_flag0
    nbjoueurs = nbjoueurs0
    depth = depth0


    def get_font(size):
        return py.font.Font("assets/vcr.ttf", size)

    while flag:
        screen.blit(BACKGROUND, (0, 0))
        MENU_MOUSE_POS = py.mouse.get_pos()
        button_list = []
        texts_button_list = ["Joueur(s): " + str(nbjoueurs),"IA depth: " + str(depth),"Eval: " + str(eval_bar_flag),
                            "FEN / PGN","Retour"]

        for i in range(len(texts_button_list)):
            button_list.append(Button(image=py.image.load("assets/midrect.png"), pos=(largeur//2 + 10, 50 + 100*i),
                                text_input=texts_button_list[i], font=get_font(35), base_color="#d4e6fc", hovering_color="White"))


        for button in button_list:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                sys.exit()
            if event.type == py.MOUSEBUTTONDOWN:
                if button_list[0].checkForInput(MENU_MOUSE_POS):
                    nbjoueurs = 1+(nbjoueurs%2)
                if button_list[1].checkForInput(MENU_MOUSE_POS):
                    depth = 1+(depth%7)
                if button_list[2].checkForInput(MENU_MOUSE_POS):
                    eval_bar_flag = not(eval_bar_flag)
                if button_list[3].checkForInput(MENU_MOUSE_POS):
                    PGN,FEN,CTRLV = pgn_or_fen()
                    run(eval_bar_flag,nbjoueurs,CTRLV,CTRLV,depth,PGN,FEN)
                if button_list[4].checkForInput(MENU_MOUSE_POS):
                    return eval_bar_flag,nbjoueurs,depth

        py.display.update()


def main():
    """Menu d'accueil"""

    flag = True
    largeur = FINAL_WIDTH
    hauteur = HEIGHT
    eval_bar_flag = True #VALEUR DE BASE
    nbjoueurs = 1 #VALEUR DE BASE
    depth = 4 #VALEUR DE BASE

    def get_font(size):
        #return py.font.SysFont("Montserrat",size,False,False)
        return py.font.Font("assets/vcr.ttf", size)

    while flag:
        screen.blit(BACKGROUND, (0, 0))
        MENU_MOUSE_POS = py.mouse.get_pos()

        PLAY_BUTTON = Button(image=py.image.load("assets/bigrect.png"), pos=(largeur//2 + 10, hauteur//2 - 100),
                            text_input="JOUER", font=get_font(80), base_color="#d4e6fc", hovering_color="White")
        OPTIONS_BUTTON = Button(image=py.image.load("assets/bigrect.png"), pos=(largeur//2 + 10, hauteur//2),
                            text_input="OPTIONS", font=get_font(80), base_color="#d4e6fc", hovering_color="White")
        QUIT_BUTTON = Button(image=py.image.load("assets/bigrect.png"), pos=(largeur//2 + 10, hauteur//2 + 100),
                            text_input="QUITTER", font=get_font(60), base_color="#d4e6fc", hovering_color="White")

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                sys.exit()
            if event.type == py.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    flag = False
                    run(eval_bar_flag,nbjoueurs,'','',depth)
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    eval_bar_flag,nbjoueurs,depth = options(eval_bar_flag,nbjoueurs,depth)
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    py.quit()
                    sys.exit()
        py.display.update()


if __name__ == "__main__":
    main()
