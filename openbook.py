import polyglot
import chess


def entrymove_to_moveLog(movefromEntry):
    ''' Prend en entrée un move donnée par une entry du module chess.polyglot
    et retourne la traduction du coup
    Peut aussi servir pour jouer le coup
    '''

    s = [c for c in str(movefromEntry)]
    ranksToRows,filesToCols = {"1": 7, "2" : 6,"3": 5,"4": 4,
                    "5": 3,"6": 2,"7": 1,"8" : 0},{"a": 0,"b": 1,"c": 2,"d": 3,
                                   "e": 4,"f": 5,"g": 6,"h": 7}
    startSq,endSq = (ranksToRows[s[1]],filesToCols[s[0]]),(ranksToRows[s[3]],filesToCols[s[2]])
    # return board.trad_move(boardbybits.Move(startSq,endSq))
    return startSq,endSq

def find_book_moves(boardchess):

    '''Prend en entrée un board au format du module chess pour le moment et
    renvoie une liste d'entry où les entry.move sont des coups d'ouvertures.
    Si la longueur de cette liste est nulle, ie 0 == sum(1 for _ in reader.find_all(board))
    alors la phase d'ouverture est finie

    exentry = Entry(key=8704797333742910878, raw_move=353, weight=14358, learn=0, move=Move.from_uci('f1b5'))
    print(exentry.move)
    print(exentry.weight)
    >>> f1b5
    >>> 14358
    '''
    boardchess = chess.Board(boardchess)
    moves = []
    with polyglot.open_reader('book\codekiddy.bin') as reader: #élement du module chess.polyglot, pas chess
        n = sum(1 for _ in reader.find_all(boardchess))  #élement du module chess.polyglot, pas chess
        if n==0:
            print("C'est vide, il faut utliser l'engine")
        else:
            for entry in reader.find_all(boardchess):  #élement du module chess.polyglot, pas chess
                mymove = entrymove_to_moveLog(entry.move)
                moves.append(mymove)
    return moves,moves!=[]
