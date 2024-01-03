import random

def findRandomMove(validMoves):
    x = validMoves[random.randint(0,len(validMoves)-1)]
    #if move.pawnPromotion:
     #   promotedPiece = "Q";
    return x

def findBestMove(gs, validMoves):
    pass