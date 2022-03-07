import pygame as p
import board
import time
import engine
import chess

vertSapin,bleuPSV,brown,whiteBrown = (30, 79, 27),(17,141,129),(184,140,100),(248,220,180)
colors = [whiteBrown,brown]

p.init()
icone = p.image.load("images/chessico.png")
p.display.set_icon(icone)
p.display.set_caption("Chess Engine")
WIDTH,HEIGHT,DIMENSION = 512,512,8 #Dimension de l'échiquier
SQ_SIZE = HEIGHT // DIMENSION #Taille des cases
MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT,MAX_FPS,IMAGES = int(HEIGHT/3),HEIGHT,30,{} #GERE LE TICK POUR LES ANIMS ETC, SI ON A BESOIN DE RAM ON LE PASSE A TRES PEU

filesToCols = {"a": 0,"b": 1,"c": 2,"d": 3,
                "e": 4,"f": 5,"g": 6,"h": 7}
colsToFiles = {v : k for k,v in filesToCols.items()}

#Initialise un dictionnaire global pour les images (une seule fois avec pygame sinon trop lourd)
def loadImages():
    pieces = ["wp","wR","wN","wB","wQ","wK","bp","bR","bN","bB","bQ","bK"]
    for piece in pieces:
        #IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE,SQ_SIZE)) #Grâce à ça, on peut appeler une image par 'IMAGES["piece"]'
        IMAGES[piece] = p.image.load("images/" + piece + ".png")



def main():
    b = board.GameState()
    p.init()
    screen,clock = p.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH,HEIGHT)),p.time.Clock()
    screen.fill(p.Color("white"))
    validMoves,moveMade,animate,running,gameOver = b.move_generation(),False,False,True,False  #TODO Servira pour jouer uniquement des coups valides!#Flag utilisé lorsqu'un move est joué (est utile pour éviter les bugs),#flag pour savoir si on doit animer,#A voir quand il y aura les mats !! #TODO ce n'est pas pour tout de suite
    loadImages() #On fait ça une seule fois avant la boucle while
    sqSelected,playerClicks = (),[] #Pas de case sélectionnée initialement, tuple(row,col) #Garder la trace des cliques de l'utilisateur (deux tuples(row,col))
    moveLogFont,coordFont = p.font.SysFont("Montserrat",20,False,False),p.font.SysFont("Montserrat",18,False,False)
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #Gestionnaire de la souris:
            elif e.type == p.MOUSEBUTTONDOWN: #Drag and drop peut-être après
                if not gameOver:
                    location = p.mouse.get_pos() #(x,y) coordonnées de la souris
                    col,row = location[0]//SQ_SIZE,location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col >= 8 or (len(playerClicks) == 0 and gs.board[row][col] == '--'): #L'utilisateur a cliqué sur la même cases ou a cliqué à côté
                        sqSelected,playerClicks = (),[]
                    else:
                        sqSelected = (row,col)
                        if sqSelected == (1,1):
                            print("JE SUIS LE FEN BOARD PARTIEL DE LA POSITION!!!!")
                            print(gs.getFen())
                        playerClicks.append(sqSelected) #On append de la même manière pour le premier et deuxième click
                    if len(playerClicks) == 2: #Après le 2nd click
                        moved = board.Move(playerClicks[0],playerClicks[1],gs.board)
                            #print(engine.find_book_moves(chess.Board('rnbqkb1r/ppp1ppp1/5n2/3p3p/3P4/5NP1/PPP1PP1P/RNBQKB1R w KQkq - 0 4')))
                        if True : #if move in validMoves:
                            tradName = gs.tradMove(moved)
                            gs.makeMove(moved,tradName)
                            moveMade,animate = True,True
                            sqSelected,playerClicks = (),[] #On reste les clicks
                            if len(gs.moveLog) >= 1:
                                print(engine.find_book_moves(gs))
                                print(engine.find_endgame_pos_val(gs))
                        else:
                            playerClicks = [sqSelected] #Petit tips : quand le deuxième click d'une première pièce n'est pas sur une case
                            #autorisée par un coup légal, la case du deuxième du click devient la case de départ !!

            #Gestionnaire du clavier
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo depuis la touche Z (peut être changé)
                    gs.undoMove()
                    moveMade,animate = True,False
                if e.key == p.K_r: #Rester le board avec la touche 'r'
                    gs.__init__()
                    validMoves,sqSelected,playerClicks = gs.getValidMoves(),(),[]
                    moveMade,animate = False,False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock,coordFont)
                validMoves,moveMade,animate = gs.getValidMoves(),False,False
        drawGameState(screen,gs,validMoves,sqSelected,moveLogFont,coordFont)
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen,gs,validMoves,sqSelected): #Surligne les cases légales pour une pièce sélectionnée
    if sqSelected != ():
        r,c = sqSelected
        if True: #(gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):) #Ici il faut faire un test sur le trait
            #On la surligne!
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100) #valeur de transparence (0 = transparent, 255 = opaque)
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            #On surligne sur les cases légales pour la pièce
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))

def drawGameState(screen,gs,validMoves,sqSelected,moveLogFont,coordFont):
    drawBoard(screen,coordFont) #Dessine le drawBoard
    #On peut ajouter des trucs (surligner les cases etc)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board) #Dessine les pièces
    drawMoveLog(screen,gs,moveLogFont)
    #print("Je draw et je tourne en boucle")


def drawBoard(screen,font):
    #colors = [p.Color("White"),vertSapin]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color,case = colors[((r+c)%2)],p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE) #Petite astuce mathématique !
            p.draw.rect(screen,color,case)
            if r == 7:
                text = colsToFiles[c]
                textObject,textLocation = font.render(text,True,colors[((r+c)%2)-1]),case.move(SQ_SIZE-10,SQ_SIZE-13) #Comme ca ca décale
                screen.blit(textObject,textLocation)
            if c == 0:
                text = str(DIMENSION-r)
                textObject,textLocation = font.render(text,True,colors[((r+c)%2)-1]),case.move(3,2) #Comme ca ca décale
                screen.blit(textObject,textLocation)

def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #SI LENDROIT OU ON LA POSE EST DIFFERENT DE VIDE
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE))

def drawMoveLog(screen,gs,font):
    moveLogRect,moveLog,moveTexts = p.Rect(WIDTH,0,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT),gs.moveLogAffiche,[] #Début,début,taille, taille
    p.draw.rect(screen,p.Color("black"),moveLogRect)
    for j in range(0,len(moveLog),2): #Pour avoir 1. e4 e5 2. Nc3 Nf6
        moveString = ' ' + str(j//2 + 1) + '. ' + moveLog[j] + ' '
        if j+1 < len(moveLog):
            moveString += moveLog[j+1]
        moveTexts.append(moveString)
    movesPerRow,padding,lineSpacing = 2,5,2 #Choix arbitraire de mettre un nb de moves sur les lignes
    textY = padding
    for i in range(0,len(moveTexts),movesPerRow):
        text = " "
        for k in range(movesPerRow):
            if i+k < len(moveTexts):
                text += moveTexts[i+k] + " "
        textObject,textLocation = font.render(text,True,p.Color('white')),moveLogRect.move(padding,textY)#Comme ca ca décale
        screen.blit(textObject,textLocation)
        textY += textObject.get_height() + lineSpacing


def animateMove(move,screen,board,clock,font): #C'est pas le plus opti mais oklm ça fonctionne que 1s
    dR,dC = move.endRow-move.startRow,move.endCol-move.startCol
    framesPerSquare = 10 #nombre de frame pour le move
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r,c = (move.startRow + dR*frame/frameCount,move.startCol + dC*frame/frameCount)
        drawBoard(screen,font)
        drawPieces(screen,board)
        color,endSquare = colors[(move.endRow + move.endCol) % 2],p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        if (move.pieceCaptured != '--'):
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(480)
    '''print("Je me mets en pause!")
    t = board.test()
    time.sleep(10)
    t.modiflag()
    On peut mettre ici move_engine()'''

if __name__ == "__main__":
    main()
