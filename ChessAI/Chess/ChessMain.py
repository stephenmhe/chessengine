import pygame as p
import ChessEngine
import RRIO

BOARD_WIDTH = BOARD_HEIGHT = 512
LOG_PANEL_WIDTH = 250
LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def loadImages():
    pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load( piece + ".png"), (SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH+LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    moveLogFont = p.font.SysFont("Arial", 14 , False, False)

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True #human
    playerTwo = False  #AI

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]// SQ_SIZE
                    row = location[1]// SQ_SIZE
                    if sqSelected == (row, col) or col>=8:
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #press z to undo
                    gs.undoMove()
                    moveMade = True  
                    animate = False  
                if e.key == p.K_r: #reset the board with r
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected= ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if not gameOver and not humanTurn:
            AIMove = RRIO.findRandomMove(validMoves)
            if move.pawnPromotion:
                print ("Q")
            gs.makeMove(AIMove)
        
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkamte')
            else: 
                drawText (screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected !=():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s,(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
            

def drawGameState(screen, gs, validMoves, sqSelected,moveLogFont):
    drawBoard(screen)
    highlightSquares(screen,gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen,gs,moveLogFont)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("light green")]
    for r in range (DIMENSION):
        for c in range (DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range (DIMENSION):
        for c in range (DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move,screen,board,clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCount = (abs(dR)+abs(dC))* framesPerSquare
    for frame in range(frameCount+1):
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC * frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow* SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        if move.pieceCaptured != '--':
            if move.enPassant:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow -1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32 , True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0,0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject = font.render(text,0,p.Color('Black'))
    screen.blit(textObject, textLocation.move(2,2))

def drawMoveLog(screen,gs,font):
    moveLogRect = p.Rect(BOARD_WIDTH,0,LOG_PANEL_WIDTH, LOG_PANEL_HEIGHT)
    p.draw.rect(screen,p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0,len(moveLog),2):
        moveString = str(i//2 +1)+". " + str(moveLog[i]) + " "
        if i+1 <len(moveLog):
            moveString += str(moveLog[i+1])+"  "
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 5
    lineSpace = 2
    textspace = padding
    for i in range(0,len(moveTexts),movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j <len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text,True,p.Color('white'))
        textLocation = moveLogRect.move(padding,textspace)
        screen.blit(textObject, textLocation)
        textspace += textObject.get_height() + lineSpace

if __name__ == "__main__":                
    main()