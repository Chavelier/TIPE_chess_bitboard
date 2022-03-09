import pygame as p
import board
import time
import chess





def main():












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



    '''print("Je me mets en pause!")
    t = board.test()
    time.sleep(10)
    t.modiflag()
    On peut mettre ici move_engine()'''
