import pygame
import numpy as np
import pandas as pd
import sys
import os
import csv
from datetime import datetime
import random
import Eng_2 as eng
import time
from dataclasses import dataclass

thisdir = os.getcwd()
path = thisdir + '\\files\\'

intColour1 = 'burlywood'
intColour2 = 'Black'

squares = 8
rectsize = 99
squaresize = 100
size = (800, 800)

moves = np.zeros((60, squares, squares), dtype=int)

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

verbose = False
Use_Pattern_Match = True

def mainx(this_game_id):

    board = initboard(False)

    patterns_csv = LoadPatterns('patterns.csv')
    patterns = np.asarray(patterns_csv)

    ipatterns = Load_I_Patterns('iboards.csv')

    pygame.init()
    pygame.font.init()

    myfont = pygame.font.SysFont('Comic Sans MS', 30)

    screen = pygame.display.set_mode(size)

    Queen_Move = True

    Game_on = DrawScreen(screen, board, myfont, False, board)

    move = 0
    moves[move] = board
    Winner = 'No one'

    while Game_on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game_on = False

            if event.type == pygame.KEYDOWN and Queen_Move:

                if event.key == 115: # s
                    SaveStart(board)

                if event.key == 8: # backspace
                    if verbose:
                        print('Backspace')

                    move -=2
                    if verbose:
                        print(f'Move {move}')
                        print('change')

                    prevb = board.copy()

                    if verbose:
                        print(board - moves[move])
                    board = moves[move]
                    if verbose:
                        print(board)

                    Game_on = DrawScreen(screen, board, myfont, Queen_Move, prevb)

            if event.type == pygame.MOUSEBUTTONUP and Queen_Move:

                mpos = pygame.mouse.get_pos()

                mposy = int(mpos[0] / squaresize)
                mposx = int(mpos[1] / squaresize)

                pos = GetPositions(board)
                qposx = int(pos[0,4])
                qposy = int(pos[1,4])

                #Legal square, within 1, not occupied
                QLegalMove = True if ((mposx+mposy) % 2) == 0 \
                    and abs(mposx - qposx) == 1 \
                    and abs(mposy - qposy) == 1 \
                    and board[mposx, mposy] == 0 \
                        else False

                if QLegalMove:

                    prevb = board.copy()

                    board[qposx, qposy] = 0
                    board[mposx, mposy] = 5

                    Winner = 'Queen'

                    Game_on = DrawScreen(screen, board, myfont, Queen_Move, prevb)
                    move +=1
                    moves[move] = board
                    if verbose:
                        print(f'Human - move {move}')

                    Queen_Move = False
                else:
                    if verbose:
                        print('bad move')

                SaveThisGame(moves, move, this_game_id, Winner)

        if not Queen_Move:  #pawn move

            pygame.display.set_caption('Thinking ...')

            prevb = board.copy()

            board = ComputerMove(board, patterns, ipatterns)

            Game_on = DrawScreen(screen, board, myfont, Queen_Move, prevb)
            move +=1
            moves[move] = board

            if verbose:
                print(f'Computer - move {move}')

            Queen_Move = True

            pygame.display.set_caption('Ok')

            if np.array_equal(board,prevb):
                Winner = 'Queen'
                Game_on = False

            SaveThisGame(moves, move, this_game_id, Winner)

    KeepPlaying = GameOver(screen, myfont, Winner,board)
    return KeepPlaying

def GameOver(screen, myfont, Winner,board):
    pos = GetPositions(board)
    minx = int(min(pos[0][0:4]))
    qx = int(pos[0][4])
    qy = int(pos[1][4])

    if qx <= minx:
        Winner = 'Queen'
    else:
        Winner = 'Pawns'

    pygame.display.set_caption(f'Game over - winner is {Winner}')
    textsurface = myfont.render(f'Game over - winner is {Winner}', False, 'Red')
    screen.blit(textsurface,(2*squaresize+5, 2*squaresize+25))
    textsurface = myfont.render(f'Play agian (y/n)?', False, 'Red')
    screen.blit(textsurface,(3*squaresize+5, 3*squaresize+25))
    pygame.display.flip()

    Waiting = True

    while Waiting:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Waiting = False

            if event.type == pygame.KEYDOWN:

                print(f'Key pressed is {event.key}')

                if event.key == 120: # x
                    Waiting = False
                    break

                if event.key == 110: # n
                    Waiting = False
                    break

                if event.key == 121: # y
                    Waiting = False
                    return True

def Load_I_Patterns(filename):
    patterns = []
    with open(thisdir+'\\files\\'+filename, 'r') as f:
        f_reader = csv.reader(f, delimiter='\t')

        for row in f_reader:
            (input, output) = row
            patterns.append([int(input), int(output)])

    return patterns

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

def randTF():
    return random.randint(0, 1)

def rand(min,max):
    return random.randint(min, max)

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

def SaveStart(board, filename ='start.csv'):
    backup(board)
    reshaped = np.resize(board, (1,8,8))
    reshaped = reshaped.tolist()
    with open(path+filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(reshaped)

def SaveThisGame(moves,move, this_game_id, Winner):
    filename = f'this_game_moves.csv'
    dfg = pd.DataFrame(columns=['game_id', 'move_id', 'position', 'squares'])
    vals = []
    save_moves = moves[0:move+1,:,:]

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
    currdir = os.getcwd()
    dfg.to_csv(currdir+'\\'+filename, index=False)

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

def DrawScreen(screen, board, myfont, Queen_Move, prevb):

    if np.array_equal(board,prevb):
        if verbose:
            print('no change')

    Possibles = CalcHumanMove(board)
    PossibleMoves = np.asarray(Possibles)

    xboard = board.transpose()

    if not Queen_Move:
        cb = board - prevb
        cbx = cb.transpose()
        op = np.where(cbx == -1)
        npos = np.where(cbx == 1)
        if len(op[0]) > 0:
            opxy = [op[0][0],op[1][0]]
            npxy = [npos[0][0],npos[1][0]]
            pygame.draw.rect(screen, 'Blue', [opxy[0]*squaresize, opxy[1]*squaresize, rectsize, rectsize], 2)
            pygame.display.flip()
            time.sleep(.25)

            pygame.draw.rect(screen, 'Blue', [npxy[0]*squaresize, npxy[1]*squaresize, rectsize, rectsize], 2)
            pygame.display.flip()
            time.sleep(.25)

    for x in range(0,squares):
        for y in range(0,squares):
            intColour = intColour1 if ((x+y) % 2) == 0 else intColour2
            pygame.draw.rect(screen, intColour, [x*squaresize, y*squaresize, rectsize, rectsize], 0)

            if 0 < xboard[x,y] < 5: #pawn move
                pygame.draw.circle(screen, 'black', (x*squaresize + squaresize/2 + 3, y*squaresize + squaresize/2 + 3), 30, width=2)
                pygame.draw.circle(screen, 'dodgerblue4', (x*squaresize + squaresize/2, y*squaresize + squaresize/2), 30, 0)
                pygame.draw.circle(screen, 'black', (x*squaresize + squaresize/2 + 2, y*squaresize + squaresize/2 + 2), 15, width=2)
                pygame.draw.circle(screen, 'dodgerblue3', (x*squaresize + squaresize/2, y*squaresize + squaresize/2), 15, 0)

            elif xboard[x,y] == 5:
                pygame.draw.circle(screen, 'black', (x*squaresize + squaresize/2 + 3, y*squaresize + squaresize/2 + 3), 30, width=2)
                pygame.draw.circle(screen, 'firebrick1', (x*squaresize + squaresize/2, y*squaresize + squaresize/2), 30, 0)
                pygame.draw.circle(screen, 'black', (x*squaresize + squaresize/2 + 2, y*squaresize + squaresize/2 + 2), 15, width=2)
                pygame.draw.circle(screen, 'firebrick3', (x*squaresize + squaresize/2, y*squaresize + squaresize/2), 15, 0)

    if not Queen_Move:
        Possibles = CalcHumanMove(board)
        PossibleMoves = np.asarray(Possibles)

        colour = 'firebrick'
        for z in range(0,PossibleMoves.shape[0]):
            xpos = PossibleMoves[z,1]
            ypos = PossibleMoves[z,0]
            pygame.draw.rect(screen, colour, [xpos*squaresize, ypos*squaresize, rectsize, rectsize], 2)

    pos = GetPositions(board)
    minx = int(min(pos[0][0:4]))
    qx = int(pos[0][4])
    qy = int(pos[1][4])

    if qx <= minx:  #player wins
        pygame.display.set_caption(f'Game over - you win')
        return False

    pygame.display.flip()

    if PossibleMoves.shape[0] > 0:
        return True
    else:
        return False

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

try:
    KeepPlaying = True
    while KeepPlaying:
        KeepPlaying = mainx(0)
except:
    print("Error!", sys.exc_info()[0], "occurred.")
    import traceback
    traceback.print_exc()
