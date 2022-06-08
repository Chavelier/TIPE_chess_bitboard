""" MAIN """

from tkinter import *
from engine import *
import os
import pyperclip

tk = Tk()
tk.title("Chess")
tk.resizable(width=False,height=False)
tk.maxsize(2000,1000)
# auto_play = False

canvas = Canvas(tk, width=720, height=720,bd=0, highlightthickness=0)
txt = StringVar()
tabl = Label(tk,textvariable=txt)

reverse_mode = False
black_mode = False
search_depth = 4
board = Board() #création échéquier
engine = Engine() #creation engine

move_historique = [] # de la forme (depart,arrivée)

img_list = [] #liste des images à afficher (pièces)

imgfile2 = "assets/case_indic.png"
imgitem2 = PhotoImage(file=imgfile2)


def affiche_position(l=[]):
    canvas.delete("all") # NECESSAIRE POUR L'OPTIMISATION ! (sinon les images s'enpiles au fur et à mesure)
    global img_list #besoin d'etre global sinon disparition des images
    img_list = []

    mrgx = 40
    mrgy = 40
    cell = 80

    folderName="assets/pieces"
    liste=os.listdir(folderName) # =>recupere le nom de tous les fichiers d'un dossier

    # affichage case
    for j in range(8):
        for i in range(8):
            if (i+j)%2 == 0: col = '#eeeeee'
            else: col = '#27ab28'

            if (reverse_mode and board.side) or black_mode:
                nb_id = j+1
                ltr_id = 72-i
                case_id = 63-(i+8*j)
            else:
                nb_id = 8-j
                ltr_id = 65+i
                case_id = i+8*j

            canvas.create_text(mrgx//2,cell*(j+1),text=str(nb_id))
            canvas.create_text(cell*(i+1),mrgy//2,text=chr(ltr_id))
            canvas.create_rectangle(mrgx+i*cell,mrgy+j*cell,mrgx+(i+1)*cell,mrgy+(j+1)*cell,fill=col)

            if move_historique != []:
                if move_historique[-1][0] == case_id or move_historique[-1][1] == case_id:
                    canvas.create_rectangle(mrgx+i*cell,mrgy+j*cell,mrgx+(i+1)*cell,mrgy+(j+1)*cell,fill='orange',stipple="gray50")

    # affichage pieces
    for piece in range(12):
        bb = board.bitboard[piece]

        img_file = folderName+'/'+PIECE_LETTER_IMAGES[piece]+".png"
        while bb:
            case = board.ls1b_index(bb)
            if piece == k and board.side:
                case_roi = case
            elif piece == K and not board.side:
                case_roi = case
            bb = board.pop_bit(bb, case)
            if (reverse_mode and board.side) or black_mode:
                x = 7-case%8
                y= 7-case//8
            else:
                x = case%8
                y= case//8
            img_list.append((x,y,PhotoImage(file=img_file)))
    for x,y,img in img_list:
        canvas.create_image(mrgx+(x+0.5)*cell, mrgy+(y+0.5)*cell, image=img)
    if board.is_check(board.side):
            if (reverse_mode and board.side) or black_mode:
                x = 7-case_roi%8
                y= 7-case_roi//8
            else:
                x = case_roi%8
                y= case_roi//8
            canvas.create_rectangle(mrgx+x*cell,mrgy+y*cell,mrgx+(x+1)*cell,mrgy+(y+1)*cell,fill='#ff0000',stipple="gray50")
            # ma_piece = B.cases[case_id]
            # if ma_piece.nom != ma_piece.nomPiece[0]:
            #     pos = ma_piece.nomPiece.index(ma_piece.nom)-1
            #     if ma_piece.couleur == "noir":
            #         pos += 6
            #     imgfile = folderName +'/'+liste[pos] ## strchemin:str, chemin d'accès à l'image
            #     imglist += [PhotoImage(file=imgfile)]
            #     canvas.create_image(mrgx+(i+0.5)*cell, mrgy+(j+0.5)*cell, image=imglist[i+8*j])
            #     if ma_piece.nom == "ROI":
            #         if ma_piece.couleur == "blanc" and B.in_check("blanc"):
            #             canvas.create_rectangle(mrgx+i*cell,mrgy+j*cell,mrgx+(i+1)*cell,mrgy+(j+1)*cell,fill='#ff0000',stipple="gray50")
            #         elif ma_piece.couleur == "noir" and B.in_check("noir"):
            #             canvas.create_rectangle(mrgx+i*cell,mrgy+j*cell,mrgx+(i+1)*cell,mrgy+(j+1)*cell,fill='#ff0000',stipple="gray50")
            # else:
            #     imglist += [""]
    if l != []: #gestion affichage coups possibles
        for mv in l:
            pos = mv.target
            if (reverse_mode and board.side) or black_mode:
                posx = 7-pos%8
                posy = 7-pos//8
            else:
                posx = pos%8
                posy = pos//8
            canvas.create_image(mrgx+(posx+0.5)*cell, mrgy+(posy+0.5)*cell, image=imgitem2)

affiche_position()

def execute_cmd():
    cmd= cmd_bar.get()

    global reverse_mode
    global black_mode
    global move_historique
    global search_depth

    if cmd == "help":
        print("redemarer une nouvelle partie -> new")
        print("jouer un coup -> [depart][arrivee][promotion] (ex : e2e4 ou c2c1q)")
        print("annuler un coup -> undo")
        print("jouer un coup d'ordinateur à la profondeur x -> go [x]")
        print("afficher la liste des coups jouables -> moves")
        print("charger un fen -> fen rnbqkbnr/ppp2ppp/4p3/3p4/Q1PP4/8/PP2PPPP/RNB1KBNR b KQkq - 1 3 (ex)")
        print("copier le fen -> cfen")
        print("tester les performances à la profondeur x -> perf [x]")
    elif "sd" in cmd:
        search_depth = int(cmd.split()[1])
    elif "go" in cmd:
        if cmd == "go":
            depth = search_depth
        else:
            depth = int(cmd.split()[1])
        mv = engine.bot_move(depth, board)
        move_historique.append((mv.source,mv.target))
        board.make_move(mv)
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
        if move_historique != []:
            del move_historique[-1]
        board.undo_move(True)
    elif cmd == "new":
        move_historique = []
        board.init()
        engine.__init__()
    elif cmd == "quit":
        tk.quit()
    elif cmd == "getboard":
        print(E.getboard(B))
    elif cmd == "nulle_rep":
        print(E.listfen)
    elif cmd == "la_proba":
        show_proba(E)
    elif cmd == "eval" :
        print("evaluation (pour blancs) : " + str(B.evaluer("blanc")/100))
    elif cmd == "black":
        reverse_mode = False
        black_mode = not black_mode
        print("Black mode : %s"%black_mode)
    elif cmd == "reverse":
        black_mode = False
        reverse_mode = not reverse_mode
        print("Reverse mode : %s"%reverse_mode)
    elif 4 <= len(cmd) <= 5:
        coup = cmd
        if len(cmd) == 4:
            coup += " "
        mv = board.trad_move(coup)
        if mv != -1:
            move_historique.append((mv.source,mv.target))
            board.make_move(mv)


    affiche_position()
    txt.set("Eval (côté blanc) : %s"%(board.evaluation(True)/100))
    cmd_bar.delete(0,"end")
    board.is_this_end() # on teste si c'est la fin



# gestion des touches ----------------------------------------------------------

def button_push(evt=""): #se déclenche lors de l'appui sur bouton
    execute_cmd()

def on_click(evt):

    casex = (evt.x-40)//80
    casey = (evt.y-40)//80
    if -1<casex<8 and -1<casey<8:
        # if len(cmd_bar.get()) >= 4:
        #     cmd_bar.delete(0,"end")
        if (reverse_mode and board.side) or black_mode:
            coord2case = 63-(casex+8*casey)
        else:
            coord2case = casex+8*casey

        c = CASES[coord2case]
        cmd_bar.insert("end",c)
        taille_texte = len(cmd_bar.get())
        if taille_texte == 2:
            liste = board.legal_move_generation(board.side)
            l2=[]
            for mv in liste:
                if mv.source == coord2case:
                    l2.append(mv)
            if l2 != []:
                affiche_position(l2)
            else:
                cmd_bar.delete(0,"end")
        elif taille_texte >= 4:
            execute_cmd()
def on_click2(evt):
    if cmd_bar.get() == "":
        cmd_bar.insert("end","undo")
    execute_cmd()
def bot_play(evt):
    cmd_bar.delete(0,"end")
    cmd_bar.insert("end","go")
    execute_cmd()


# gestion des touches ----------------------------------------------------------
tk.bind_all('<KeyPress-Return>', button_push)
tk.bind_all('<1>', on_click)
tk.bind_all('<3>',on_click2)
# tk.bind_all('<KeyPress-Control_L>', bot_play)
tk.bind_all('<Up>', bot_play)

box = Frame(tk)
cmd_bar = Entry(box)
btn = Button(box, text='ENTRER', command=button_push)



#Pack()
box.pack(expand=YES)
cmd_bar.grid(row=0, column=0, sticky=W)
btn.grid(row=0, column=1, sticky=W)
canvas.pack()
tabl.pack()
#Pack()




tk.mainloop()
