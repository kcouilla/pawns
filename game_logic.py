import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

import Eng_2 as eng

thisdir = str(Path(__file__).resolve().parent)
path = thisdir + '\\files\\'

squares = 8

verbose = False
Use_Pattern_Match = True

@dataclass
class GameState:
    xs: list[int]
    ys: list[int]
    minx: int
    maxx: int
    qposx: int
    qposy: int
    rows: int
    gap: int

def Load_I_Patterns(filename):
    patterns = []
    with open(thisdir+'\\files\\'+filename, 'r') as f:
        f_reader = csv.reader(f, delimiter='\t')

        for row in f_reader:
            (input, output) = row
            patterns.append([int(input), int(output)])

    return patterns

def LoadPatterns(filename):

    with open(thisdir+'\\files\\'+filename, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    patterns = []
    for row in rows:
        nwrow = []
        for r in row:
            nwrow.append(eval(r))
        patterns.append(nwrow)

    return patterns

def initboard(LoadStart = False):
    board = np.zeros((squares, squares), dtype=int)

    if LoadStart:
        with open(path+'start.csv', 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)

        board_csv = []
        for row in rows:
            for r in row:
                board_csv.append(eval(r))
        board = np.asarray(board_csv)

        if verbose:
            print(board)

    else:

        for col in range(0,squares,2):
            board[0,col] = 1

        row, col = 7,3
        board[row,col] = 5

        if verbose:
            print(board)

    return board

def GetPositions(board):

    pos = np.empty([2,5], dtype=int)

    rs = np.where((0 < board) & (board < 5))
    for p in range(0,4):
        pos[0,p] = int(rs[0][p])
        pos[1,p] = int(rs[1][p])

    qpos = np.where(board == 5)
    pos[0,4] = int(qpos[0][0])
    pos[1,4] = int(qpos[1][0])

    return(pos)

def GetGameState(board):
    pos = GetPositions(board)
    #pawn positions
    ppos = pos[:,0:4]
    xs = ppos[0,:]
    ys = ppos[1,:]

    #queen position
    qposx = int(pos[0,4])
    qposy = int(pos[1,4])

    minx = int(np.min(xs))
    maxx = int(np.max(xs))
    rows = maxx - minx
    gap = qposx - maxx

    if verbose:
        print(f'qx: {qposx}, qy: {qposy}, gap: {gap}')

    this_GameState = GameState(xs, ys, minx, maxx, qposx, qposy, rows, gap)

    return this_GameState

def CalcHumanMove(board):
    QPos = np.where(board == 5)
    QPosX = int(QPos[0][0])
    QPosY = int(QPos[1][0])

    possibles = []
    for x in range(-1,2,2):
        for y in range(-1,2,2):
            if 0 <= QPosX + x <=7 and 0 <= QPosY + y <=7 and board[QPosX + x, QPosY + y] == 0:
                loc = []
                loc.append(QPosX + x)
                loc.append(QPosY + y)
                possibles.append(loc)

    return possibles

def March(board, patterns):
    nboard = board.copy()
    this_GameState = GetGameState(nboard)

    nextrow = 2 if this_GameState.rows == 0 else 1

    selectedRows = nboard[this_GameState.minx:this_GameState.maxx+nextrow,:].copy()

    #remove queen
    queen = np.where(selectedRows == 5)
    selectedRows[queen] = 0

    # compare selected rows to patterns
    MarchPattern = False
    legalMove = False
    for x in range(0,patterns.shape[0]):
        if np.array_equal(selectedRows,patterns[x]):
            MarchPattern = True
            if verbose:
                print(f'MarchPattern = True, selected pattern: {x}')
            break

    # get next position
    x +=1

    if MarchPattern:

        selectedPattern = patterns[x].copy()
        change = selectedPattern - selectedRows

        newPos = np.where(change == 1)
        newPosX = int(newPos[0][0])
        newPosY = int(newPos[1][0])

        #create function to check that move is on board as well as empty
        legalMove = nboard[newPosX + this_GameState.minx, newPosY] == 0  #unoccupied

        if legalMove:

            selectedPiecePos = np.where(change == -1)
            selectedPiecePosX = int(selectedPiecePos[0][0])
            selectedPiecePosY = int(selectedPiecePos[1][0])

            selectedPiece = nboard[selectedPiecePosX + this_GameState.minx, selectedPiecePosY]
            nboard[selectedPiecePosX + this_GameState.minx, selectedPiecePosY] = 0

            nboard[newPosX + this_GameState.minx, newPosY] = selectedPiece

        else:
            if verbose:
                print('Not legal move')
            nboard = board.copy()

    return nboard

def PatternMatchMove(board, patterns):
    if verbose:
        print('looking in')
        print(patterns)
    bint = eng.MakeInt(board)
    if verbose:
        print(f'looking for {bint}')
    matching_patterns = [p[1] for p in patterns if int(p[0]) == int(bint)]

    if matching_patterns:
        if verbose:
            print(f'got {matching_patterns[0]}')
        rboard = eng.MakeBoardFromPosition(int(matching_patterns[0]))
        if verbose:
            print(rboard)
        return rboard
    else:
        if verbose:
            print('not found')
        return board

def ComputerMove(board, patterns, ipatterns):

    GotMove = False

    if verbose:
        print('Trying March')

    nboard = March(board, patterns)
    if not np.array_equal(board,nboard):    #march succeeds
        if verbose:
            print('March succeeded')
        GotMove = True

    if Use_Pattern_Match:

        if not GotMove:

            if verbose:
                print('Trying PatternMatchMove')

            nboard = PatternMatchMove(board, ipatterns)

            if not np.array_equal(board,nboard):    #pattern succeeds
                if verbose:
                    print('Pattern match succeeded')
                GotMove = True

    if not GotMove:

        if verbose:
            print('Calculating move')
        nboard = eng.CalcMove(board)

    return nboard

def get_game_status(board):
    """Returns (game_over, winner) where winner is 'Queen', 'Pawns', or None."""
    pos = GetPositions(board)
    minx = int(min(pos[0][0:4]))
    qx = int(pos[0][4])

    if qx <= minx:
        return True, 'Queen'

    if len(CalcHumanMove(board)) == 0:
        return True, 'Pawns'

    return False, None

def backup(boards_to_write):

    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'start_{date}.csv'

    if verbose:
        print(filename)

    reshaped = np.resize(boards_to_write, (1,8,8))
    reshaped = reshaped.tolist()
    with open(path+filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(reshaped)

def SaveStart(board, filename ='start.csv'):
    backup(board)
    reshaped = np.resize(board, (1,8,8))
    reshaped = reshaped.tolist()
    with open(path+filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(reshaped)

def SaveThisGame(moves, move, this_game_id, Winner):
    filename = 'this_game_moves.csv'
    vals = []
    save_moves = np.asarray(moves)[0:move+1,:,:]

    move_id = 0
    game_id = this_game_id
    for m in save_moves:
        sq = eng.GetSquares(m)
        b = bytes(sq)
        bint = int.from_bytes(b,'big')
        thisdict = {'game_id': game_id, 'move_id': move_id, 'position': bint, 'squares': sq}
        vals.append(thisdict)
        move_id += 1

    dfg = pd.DataFrame(vals, columns = ['game_id','move_id','position','squares'])
    dfg.to_csv(thisdir+'\\'+filename, index=False)
