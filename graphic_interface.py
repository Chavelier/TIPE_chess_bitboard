import pygame as py
import board
import time
from init import *

vertSapin,bleuPSV,brown,whiteBrown = (30, 79, 27),(17,141,129),(184,140,100),(248,220,180)
colors = [whiteBrown,brown]

py.init()
icone = py.image.load("images/chessico.png")
py.display.set_icon(icone)
py.display.set_caption("Chess Engine")
WIDTH,HEIGHT,DIMENSION = 512,512,8 #Dimension de l'échiquier
SQ_SIZE = HEIGHT // DIMENSION #Taille des cases
MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT,MAX_FPS,IMAGES = int(HEIGHT/3),HEIGHT,120,{} #GERE LE TICK POUR LES ANIMS ETC, SI ON A BESOIN DE RAM ON LE PASSE A TRES PEU
colsToFiles = {0:"a", 1:"b", 2:"c", 3:"d", 4:"e", 5:"f", 6:"g", 7:"h"}
filesToCols = {v : k for k,v in colsToFiles.items()}

#Initialise un dictionnaire global pour les images (une seule fois avec pygame sinon trop lourd)
def loadImages():
    for piece in PIECE_LETTER[:-1]:
        IMAGES[piece] = py.image.load("images/" + PIECE_LETTER_IMAGES[PIECE_LETTER.index(piece)] + ".png")

def liste_to_move(l):
    """Prend en entrée une liste représentant les deux couples case arrivée/case départ
    et renvoie la traduction du coup. Ex : [(0,0),(7,7)] devient 'a8h1'"""
    s = ''
    for (row,col) in l:
        s += CASES[8*row+col]
    return s

def main():
    B = board.Board()
    py.init()
    screen,clock = py.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH,HEIGHT)),py.time.Clock()
    screen.fill(py.Color("white"))
    valid_moves,move_made,animate,running,game_over = B.move_generation(WHITE),False,False,True,False  #TODO Servira pour jouer uniquement des coups valides!#Flag utilisé lorsqu'un move est joué (est utile pour éviter les bugs),#flag pour savoir si on doit animer,#A voir quand il y aura les mats !! #TODO ce n'est pas pour tout de suite
    loadImages() #On fait ça une seule fois avant la boucle while
    sq_selected,player_clicks = (),[] #Pas de case sélectionnée initialement, tuple(row,col) #Garder la trace des cliques de l'utilisateur (deux tuples(row,col))
    moveLogFont,coordFont = py.font.SysFont("Montserrat",20,False,False),py.font.SysFont("Montserrat",18,False,False)
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
                            #print(engine.find_book_moves(chess.Board('rnbqkb1r/ppp1ppp1/5n2/3p3p/3P4/5NP1/PPP1PP1P/RNBQKB1R w KQkq - 0 4')))
                            if val_move == 1:
                                move_made,animate = True,True
                                sq_selected,player_clicks = (),[] #On reste les clicks
                        else:
                            player_clicks = [sq_selected] #Petit tips : quand le deuxième clic d'une première pièce n'est pas sur une case
                            #autorisée par un coup légal, la case du deuxième du clic devient la case de départ !!
                            animate = False
            #Gestionnaire du clavier
            elif e.type == py.KEYDOWN:
                if e.key == py.K_z: #undo depuis la touche Z (peut être changé)
                    B.undo_move(True)
                    move_made,animate = True,False
                if e.key == py.K_r: #Rester le board avec la touche 'r'
                    B = Board()
                    valid_moves,sq_selected,player_clicks = B.move_generation(WHITE),(),[]
                    move_made,animate = False,False

        if move_made:
            if animate:
                animate_move(mv,screen,B,clock,coordFont)
                valid_moves,move_made,animate = B.move_generation(B.history[-1][2]),False,False
        draw_game_state(screen,B,valid_moves,sq_selected,moveLogFont,coordFont)
        clock.tick(MAX_FPS)
        py.display.flip()

def highlight_squares(screen,B,valid_moves,sq_selected): #Surligne les cases légales pour une pièce sélectionnée
    if sq_selected != ():
        row,col = sq_selected
        if True: #(gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):) #Ici il faut faire un test sur le trait
            #On la surligne!
            s1,s2 = py.Surface((SQ_SIZE,SQ_SIZE)),py.Surface((SQ_SIZE,SQ_SIZE))
            s1.set_alpha(100) #valeur de transparence (0 = transparent, 255 = opaque)
            s2.set_alpha(50)
            s1.fill(py.Color('blue'))
            s2.fill(py.Color('green'))
            screen.blit(s1,(col*SQ_SIZE,row*SQ_SIZE))
            #On surligne sur les cases légales pour la pièce
            for move in valid_moves:
                case_depart = B.get_move_source(move)
                case_arrivee = B.get_move_target(move)
                start_row,start_col = case_depart//8,case_depart%8
                end_row,end_col = case_arrivee//8,case_arrivee%8
                if start_row == row and start_col == col:
                    screen.blit(s2,(end_col*SQ_SIZE,end_row*SQ_SIZE))


def draw_board(screen,font):
    #colors = [p.Color("White"),vertSapin]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color,case = colors[((r+c)%2)],py.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE) #Petite astuce mathématique !
            py.draw.rect(screen,color,case)
            if r == 7:
                text = colsToFiles[c]
                textObject,textLocation = font.render(text,True,colors[((r+c)%2)-1]),case.move(SQ_SIZE-10,SQ_SIZE-13) #Comme ca ca décale
                screen.blit(textObject,textLocation)
            if c == 0:
                text = str(DIMENSION-r)
                textObject,textLocation = font.render(text,True,colors[((r+c)%2)-1]),case.move(3,2) #Comme ca ca décale
                screen.blit(textObject,textLocation)

def draw_pieces(screen,B):
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



def draw_game_state(screen,B,valid_moves,sq_selected,moveLogFont,coordFont):
    draw_board(screen,coordFont) #Dessine le drawBoard
    highlight_squares(screen,B,valid_moves,sq_selected)
    #On peut ajouter des trucs (surligner les cases etc)
    draw_pieces(screen,B) #Dessine les pièces
    #draw_moveLog(screen,gs,moveLogFont) #TODO
    #print("Je draw et je tourne en boucle")


if __name__ == "__main__":
    main()
