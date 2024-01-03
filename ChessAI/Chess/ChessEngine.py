class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN","bB", "bQ", "bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR", "wN","wB", "wQ", "wK","wB","wN","wR"]
        ]
        self.moveFunctions = {"p":self.getPawnMoves, "R":self.getRookMoves, "Q": self.getQueenMoves, "N": self.getKnightMoves, "B":self.getBishopMoves, "K":self.getKingMoves}
        self.moveLog = []
        self.whiteToMove = True
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        self.castleRightsLog = [CastleRights(self.whiteCastleKingside, self.blackCastleKingside, self.whiteCastleQueenside, self.blackCastleQueenside)]

    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol]= "--"
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved =="wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved =="bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow)//2, move.endCol)
        else: 
            self.enPassantPossible = ()
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"
        if move.pawnPromotion:
            promotedPiece = input("Promote to Queen (Q), Rook (R), Bishop (B), or Knight (N):")
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        if move.castle:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol -1 ] = self.board[move.endRow][move.endCol +1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:
                self.board[move.endRow][move.endCol + 1 ] = self.board[move.endRow][move.endCol -2]
                self.board[move.endRow][move.endCol - 2] = '--'
        self.enPassantPossibleLog.append(self.enPassantPossible)

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.whiteCastleKingside, self.blackCastleKingside, self.whiteCastleQueenside,self.blackCastleQueenside))
 
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved =="wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved =="bK":
                self.blackKingLocation = (move.startRow, move.startCol) 

            if move.enPassant:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            self.castleRightsLog.pop()
            castleRights = self.castleRightsLog[-1]
            self.whiteCastleKingside = castleRights.wks
            self.whiteCastleQueenside = castleRights.wqs
            self.blackCastleKingside = castleRights.bks
            self.blackCastleQueenside = castleRights.bqs

            if move.castle:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1 ] = self.board[move.endRow][move.endCol -1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol -2 ] = self.board[move.endRow][move.endCol +1]
                    self.board[move.endRow][move.endCol +1] = '--'

            self.checkmate = False
            self.stalemate = False

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else: 
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)
        return moves
    
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):    
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation
        pawnPromotion = False

        if self.board[r+moveAmount][c] == "--":
            if not piecePinned or pinDirection == (moveAmount,0):
                if r+moveAmount == backRow:
                    pawnPromotion = True
                moves.append(Move((r,c),(r+moveAmount,c),self.board, pawnPromotion = pawnPromotion))
                if r== startRow and self.board[r+2*moveAmount][c] == "--":
                    moves.append(Move((r,c),(r+2*moveAmount,c), self.board))
        if c-1 >= 0:
            if not piecePinned or pinDirection == (moveAmount,-1):
                if self.board[r+moveAmount][c-1][0] == enemyColor:
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r,c),(r+moveAmount,c-1),self.board, pawnPromotion = pawnPromotion))
                if (r + moveAmount, c-1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol <c:
                            insideRange = range(kingCol +1, c-1)
                            outsideRange = range(c+1, 8)
                        else:
                            insideRange = range(kingCol -1,c,-1)
                            outsideRange = range(c-2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i]!='--':
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square [0] == enemyColor and (square[1]=="R" or square[1]=="Q"):
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c),(r+moveAmount, c-1), self.board, enPassant = True))
        if c+1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r+moveAmount][c+1][0] == enemyColor:
                    if r+moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r,c),(r+moveAmount,c+1),self.board, pawnPromotion = pawnPromotion))
                if (r+moveAmount, c +1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol <c:
                            insideRange = range(kingCol +1, c)
                            outsideRange = range(c+2, 8)
                        else:
                            insideRange = range(kingCol -1,c+1,-1)
                            outsideRange = range(c-1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i]!='--':
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square [0] == enemyColor and (square[1]=="R" or square[1]=="Q"):
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r,c),(r+moveAmount, c+1), self.board, enPassant = True))

    def getRookMoves(self, r,c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1]!= 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r+d[0] *i
                endCol = c+d[1] *i
                if 0<= endRow <8 and 0<= endCol <8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getBishopMoves(self, r,c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        bishopMoves = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in bishopMoves:
            for i in range(1,8):
                endRow = r+d[0]*i
                endCol = c+d[1]*i
                if 0<= endRow<8 and 0<= endCol <8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0],-d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r,c),(endRow,endCol),self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getQueenMoves(self, r,c, moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKnightMoves(self, r,c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r+m[0]
            endCol = c+m[1]
            if 0<=endRow <8 and 0<= endCol <8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r,c),(endRow,endCol), self.board))

    def getKingMoves(self, r,c, moves):
        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r+rowMoves[i]
            endCol = c+colMoves[i]
            if 0<=endRow <8 and 0<= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                       moves.append(Move((r,c),(endRow,endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (r,c)
                    else:    
                        self.blackKingLocation = (r,c)
        self.getCastleMoves(r,c,moves,allyColor)

    def getCastleMoves(self,r,c,moves,allyColor):
        inCheck = self.squareUnderAttack(r,c,allyColor)
        if inCheck:
            print("Check")
            return
        if(self.whiteToMove and self.whiteCastleKingside) or (not self.whiteToMove and self.blackCastleKingside):
            self.getKingsideCastleMoves(r,c,moves,allyColor)
        if(self.whiteToMove and self.whiteCastleQueenside) or (not self.whiteToMove and self.blackCastleQueenside):
            self.getQueensideCastleMoves(r,c,moves,allyColor)
    
    def getKingsideCastleMoves(self,r,c,moves, allyColor):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--' and \
         not self.squareUnderAttack(r, c+1, allyColor ) and not self.squareUnderAttack(r, c+2, allyColor):
            moves.append(Move((r,c),(r,c+2),self.board, castle = True))
    
    def getQueensideCastleMoves (self,r,c,moves,allyColor):
        if self.board[r][c-1] =='--' and self.board[r][c-2]=='--' and self.board[r][c-3]== '--' and\
         not self.squareUnderAttack(r,c-1, allyColor) and not self.squareUnderAttack(r,c-2,allyColor):
            moves.append(Move((r,c),(r,c-2),self.board,castle=True))

    def squareUnderAttack(self,r,c,allyColor):
        enemyColor = 'w' if allyColor =='b' else 'b'
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1,8):
                endRow = r+d[0]*i
                endCol = r+d[1]*i
                if 0<= endRow <8 and 0<= endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0<=j <= 3 and type =='R') or \
                                (4<= j <= 7 and type =='B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6<= j <=7) or (enemyColor =='b' and 4<= j <= 5))) or \
                                (type =='Q') or (i ==1 and type =='K'):
                            return True
                        else:
                            break
                else:
                    break
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0<= endRow <8 and 0<= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] =='N':
                    return True
        return False

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0<= endRow <8 and 0 <= endCol <8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0<=j <= 3 and type =='R') or \
                                (4<= j <= 7 and type =='B') or \
                                (i ==1 and type == 'p' and ((enemyColor == 'w' and 6<= j <=7) or (enemyColor =='b' and 4<= j <= 5))) or \
                                (type =='Q') or (i ==1 and type =='K'):
                            if possiblePin ==():
                                inCheck=True
                                checks.append((endRow, endCol, d[0],d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else: 
                            break
                else:
                    break
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0<= endRow <8 and 0<= endCol <8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] =='N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks
    
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.whiteCastleKingside = False
            self.whiteCastleQueenside = False
        elif move.pieceMoved =='bK':
            self.blackCastleKingside = False
            self.blackCastleQueenside = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 7:
                    self.whiteCastleKingside = False
                elif move.startCol == 0:
                    self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 7:
                    self.blackCastleKingside = False
                elif move.startCol == 0:
                    self.blackCastleQueenside = False
        
        if move.pieceCaptured =='wR':
            if move.endRow ==7:
                if move.endCol ==0:
                    self.whiteCastleQueenside = False
                elif move.endCol ==7:
                    self.whiteCastleKingside = False
        if move.pieceCaptured =='bR':
            if move.endRow ==0:
                if move.endCol ==0:
                    self.blackCastleKingside = False
                elif move.endCol ==7:
                    self.lackCastleQueenside = False


class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    ranksToRows = {"8":0, "1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g" :6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant = False, pawnPromotion = False, castle = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.enPassant = enPassant
        self.pawnPromotion = pawnPromotion
        self.castle = castle
        if enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'
        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow *1000 + self.startCol*100 + self.endRow *10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]    
    
    def __str__(self):
        if self.castle:
            return "O-O" if self.endCol ==6 else "O-O-O"
        endSquare = self.getRankFile (self.endRow, self.endCol)
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol]+"x"+ endSquare
            else:
                return endSquare
            
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString +="x"
        return moveString + endSquare