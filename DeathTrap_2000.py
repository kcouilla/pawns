############################
# auto-py-to-exe
############################

import pygame
import numpy as np
import pandas as pd
import sys
import os
import csv
from datetime import datetime
import random
import CalcComputerMove as ccm
import Eng_2 as eng
import basic_stuff as bs
import time

thisdir = os.getcwd()
path = thisdir + '\\files\\'

intColour1 = 'burlywood'
intColour2 = 'Black'
green = (0, 255, 0)
blue = (0, 0, 128)

squares = 8
rectsize = 99
squaresize = 100
size = (800, 800)

moves = np.zeros((60, squares, squares), dtype=int)
move = 0

save_board = np.zeros((squares, squares), dtype=int)

from dataclasses import dataclass

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
    # b: float 
    # t: float

Game_on = True
verbose = False
Use_Pattern_Match = True

def mainx(this_game_id):

    # board = initboard(True)
    board = initboard(False)

    patterns_csv = LoadPatterns('patterns.csv')
    patterns = np.asarray(patterns_csv)

    # patternsq_csv = LoadPatterns('newboards.csv')
    # patternsq = np.asarray(patternsq_csv)

    ipatterns = Load_I_Patterns('iboards.csv')
    # print(ipatterns)

    pygame.init()  
    pygame.font.init()

    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    
    screen = pygame.display.set_mode(size)

    Queen_Move = True

    Game_on = DrawScreen(screen, board, myfont, False, board)
    # Game_on = DrawScreen(screen, board, myfont, Queen_Move, board)

    # Game_on = True
    
    move = 0
    moves[move] = board
    Winner = 'No one'
    # move +=1

    while Game_on:
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                # SaveGame(moves, move)
                Game_on = False 

            if event.type == pygame.KEYDOWN and Queen_Move:

                # pos = GetPositions(board)
                # # print(pos)
                # minx = int(min(pos[0][0:4]))
                # qx = int(min(pos[0][4:5]))
                # if qx <= minx:  #player wins
                #     pygame.display.set_caption(f'Game over - you win')
                #     Game_on = DrawScreen(screen, board, myfont)

                if event.key == 115: # s
                    # board_to_save[0] = board
                    SaveStart(board)

                if event.key == 8: # backspace
                    if verbose:
                        print('Backspace')
                    # for m in range(0,moves.shape[0]):
                    #     if np.sum(moves[m]) > 0:
                    #         print(m)
                    #         print(moves[m])
                   
                    # print(board)
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

                # Possibles = CalcHumanMove(board)
                # PossibleMoves = np.asarray(Possibles)
                # aposs = poss.transpose()

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

                    # print(board)

                    Winner = 'Queen'
            
                    Game_on = DrawScreen(screen, board, myfont, Queen_Move, prevb)
                    move +=1
                    moves[move] = board
                    if verbose:
                        print(f'Human - move {move}')
                    # print(board.transpose())

                    Queen_Move = False
                else:
                    if verbose:
                        print('bad move')

                SaveThisGame(moves, move, this_game_id, Winner)

        if not Queen_Move:  #pawn move

            # print(board)

            pygame.display.set_caption('Thinking ...')

            prevb = board.copy()

            board = ComputerMove(board, patterns, ipatterns)

            # if np.array_equal(board,prevb):
            #     Winner = 'Queen'
            
            Game_on = DrawScreen(screen, board, myfont, Queen_Move, prevb)
            move +=1
            moves[move] = board
            
            if verbose:
                print(f'Computer - move {move}')

            Queen_Move = True

            pygame.display.set_caption('Ok')

            # qm = eng.CalcQueenMove(board)
            if np.array_equal(board,prevb):
                Winner = 'Queen'
                Game_on = False

            SaveThisGame(moves, move, this_game_id, Winner)

    KeepPlaying = GameOver(screen, myfont, Winner,board)
    return KeepPlaying
    print('game over')

def GameOver(screen, myfont, Winner,board):
    pos = GetPositions(board)
    # print(pos)
    minx = int(min(pos[0][0:4]))
    # qx = int(pos[0][4:5])
    # qy = int(pos[1][4:5])
    qx = int(pos[0][4])
    qy = int(pos[1][4])

    if qx <= minx:
        Winner = 'Queen'
    else:
        Winner = 'Pawns'

    pygame.display.set_caption(f'Game over - winner is {Winner}')
    # pygame.draw.rect(screen, 'Yellow', [4*squaresize, 4*squaresize, rectsize, rectsize], 2)
    textsurface = myfont.render(f'Game over - winner is {Winner}', False, 'Red')
    screen.blit(textsurface,(2*squaresize+5, 2*squaresize+25))
    textsurface = myfont.render(f'Play agian (y/n)?', False, 'Red')
    screen.blit(textsurface,(3*squaresize+5, 3*squaresize+25))
    pygame.display.flip()

    Waiting = True

    while Waiting:
    
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                # SaveGame(moves, move)
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
                    break


    #     if event.type == pygame.KEYDOWN and Queen_Move:

    #         # pos = GetPositions(board)
    #         # # print(pos)
    #         # minx = int(min(pos[0][0:4]))
    #         # qx = int(min(pos[0][4:5]))
    #         # if qx <= minx:  #player wins
    #         #     pygame.display.set_caption(f'Game over - you win')
    #         #     Game_on = DrawScreen(screen, board, myfont)

    #         if event.key == 115: # s

    # time.sleep(5)

def Load_I_Patterns(filename):
    patterns = []
    with open(thisdir+'\\files\\'+filename, 'r') as f:
    # with open(path+filename, 'r') as f:
        f_reader = csv.reader(f, delimiter='\t')

        for row in f_reader:
            (input, output) = row
            # print(f"if {input} then {output}")
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
        # return nboard

    # # Get Move

    if Use_Pattern_Match:

        if not GotMove:

            if verbose:
                print('Trying PatternMatchMove')

            nboard = PatternMatchMove(board, ipatterns)

            if not np.array_equal(board,nboard):    #pattern succeeds
                if verbose:
                    print('Pattern match succeeded')
                GotMove = True
                # return nboard

    if not GotMove:        

        if verbose:
            print('Calculating move')
        # nboard = ccm.CalcMove(board)
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
        # bs.ShowBoard(rboard)
        if verbose:
            print(rboard)
        return rboard
    else:
        if verbose:
            print('not found')
        return board
        

def xPatternMatchMove(board, patternsq):

    nboard = board.copy()

    nzboard = np.nonzero(nboard)
    #minx, maxx includes queen, so need to reselect
    minx, maxx = min(nzboard[0]), max(nzboard[0])
    sel_board = board[minx:maxx+1,:].copy()

    # print('sel_board')
    # print(sel_board)

    pawns = np.where((sel_board > 0) & (sel_board < 5))

    foundPattern = False

    for x in range(0,patternsq.shape[0]):
        nzboard = np.nonzero(patternsq[x])
        pminx, pmaxx = min(nzboard[0]), max(nzboard[0])
        # print(f'minx: {minx}, maxx: {maxx}, pminx: {pminx}, pmaxx: {pmaxx}')
        match_pattern = patternsq[x,pminx:pmaxx+1,:].copy()

        #not needed, since all pawns 1
        # pawns = np.where((match_pattern > 0) & (match_pattern < 5))
        # match_pattern[pawns] = 1

        if np.array_equal(sel_board,match_pattern):
            foundPattern = True
            # print(f'current board')
            # print(sel_board)
            # print(f'selected patternq: {x}')
            # print(match_pattern)
            break

    if foundPattern:

        nzboard = np.nonzero(patternsq[x])

        minx, maxx = min(nzboard[0]), max(nzboard[0])
        sel_board = nboard[minx:maxx+1,:].copy()
        # temp remove, don't recalc pminx and pmaxx
        pminx1, pmaxx1 = min(nzboard[0]), max(nzboard[0])

        x +=1

        # print('Move to')
        # print(patternsq[x])

        nzboard = np.nonzero(patternsq[x])
            # temp remove, don't recalc pminx and pmaxx
        pminx2, pmaxx2 = min(nzboard[0]), max(nzboard[0])
        # print(f'minx: {minx}, maxx: {maxx}, pminx2: {pminx2}, pmaxx2: {pmaxx2}')

        # pminx=min(pminx1,pminx2)
        # pmaxx=max(pmaxx1, pmaxx2)
        pminx, pmaxx = min(pminx1,pminx2), max(pmaxx1, pmaxx2)

        # temp remove
        sel_pattern = patternsq[x,pminx:pmaxx+1,:]
        sel_board = board[minx:minx+(pmaxx-pminx)+1,:].copy()
        # temp remove

        # print(f'minx: {minx}, maxx: {maxx}, pminx: {pminx}, pmaxx: {pmaxx}')
        
        # print('board')
        # print(sel_board)
        # print('pattern')
        # print(sel_pattern)

        change = sel_pattern - sel_board 

        # print('change')
        # print(change)

        # print(f'changes {np.count_nonzero(change != 0)}')
        if np.count_nonzero(change != 0) != 2:
            return board

        selectedPiecePos = np.where(change < 0)
        selectedPiecePosX = int(selectedPiecePos[0][0])
        selectedPiecePosY = int(selectedPiecePos[1][0])

        selectedPiece = board[selectedPiecePosX + minx, selectedPiecePosY]
        nboard[selectedPiecePosX + minx, selectedPiecePosY] = 0

        newPos = np.where(change > 0)
        newPosX = int(newPos[0][0])
        newPosY = int(newPos[1][0])

        nboard[newPosX + minx, newPosY] = selectedPiece

    return nboard


def x_CalcComputerMove(board, patterns, patternsq):
    #check for gap
    #if exists, block
    #if no gap, check for move that doesn't create a gap
    Logic = 'start'

    if GapExists(board):
        print('Gap exists')
        nboard = BlockGap(board)
        if np.array_equal(board,nboard):
            print('BlockGap failed, try level 2')
            #not blocked
            x = 1
            nboard = Level2Block(board)

            if np.array_equal(board,nboard):
                print('Level2Block failed - random move')
                nboard = RandomMove(board)
            #     no solution - random move
        else:
            print('BlockGap succeeded')
    else:   #no gap
        # nboard = GapLessMove(board)
        nboard = March(board, patterns)
        if np.array_equal(board,nboard):    #didn't find gapless move
            print('March failed - Try GapLess')
            nboard = GapLessMove(board)
            if np.array_equal(board,nboard):
                print('GapLessMove failed - random move')
                nboard = RandomMove(board)
        else:
            print('March succeeded')
    return nboard

def March(board, patterns):
    nboard = board.copy()
    this_GameState = GetGameState(nboard)

    nextrow = 2 if this_GameState.rows == 0 else 1

    selectedRows = nboard[this_GameState.minx:this_GameState.maxx+nextrow,:].copy()

    #remove queen
    queen = np.where(selectedRows == 5)
    selectedRows[queen] = 0

    #change pawn numbers to 1 - no longer needed
    # nzboard = np.nonzero(selectedRows)
    # selectedRows[nzboard] = 1

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

            nboard[newPosX + this_GameState.minx, newPosY] = selectedPiece   #not needed, since all pawns 1

        else:
            if verbose:
                print('Not legal move')
            nboard = board.copy()
            
    return nboard

def RandomMove(board):
    nboard = board.copy()
    GetMove = True
    while GetMove:

        UseIndex = rand(0,3)
        LR = randTF()
        pos = GetPositions(nboard)
        xs = pos[0][0:4]
        ys = pos[1][0:4]

        if xs[UseIndex] < 7:
            newX = xs[UseIndex] + 1 
            newY = ys[UseIndex] + 1 if LR and ys[UseIndex] < 7 else ys[UseIndex] - 1

            if nboard[int(newX), int(newY)] == 0:
                GetMove = False

    nboard[int(xs[UseIndex]), int(ys[UseIndex])] = 0
    nboard[int(newX), int(newY)] = 1
    if verbose:
        print(nboard)

    # return nboard

def GapLessMove(board):
    pos = GetPositions(board)
    px = pos[0][0:4]
    py = pos[1][0:4]

    m = 0
    for pawn in range(0,4):
        p = [px[pawn],py[pawn]]
        for L1 in range(-1,2,2):
            L1m = [int(p[0]+1),int(p[1]+L1)]
            
            if p[0] < 7 and 0 <= p[1]+L1 <= 7:
                if board[L1m[0],L1m[1]] == 0:
                    if verbose:
                        print(f'move from {p} to {L1m}')
                    nboard = MakeBoard(board.copy(),p,L1m)
                    if not GapExists(nboard):
                        break

        else:
            continue
        break
    return nboard
        
def Level2Block(board):
    boards = np.zeros((8, 8, 8), dtype=int)
    pos = GetPositions(board)
    px = pos[0][0:4]
    py = pos[1][0:4]

    m = 0
    for pawn in range(0,4):
        p = [px[pawn],py[pawn]]
        for L3 in range(-1,2,2):
            L3m = [int(p[0]+1),int(p[1]+L3)]
            
            if p[0] < 7 and 0 <= p[1]+L3 <= 7:
                if board[L3m[0],L3m[1]] == 0:
                    if verbose:
                        print(f'move from {p} to {L3m}')
                    b = MakeBoard(board.copy(),p,L3m)
                    boards[m] = b
                    m += 1

    #track queen moves to boards
    ls = np.zeros((32), dtype=int)
    # queen moves
    qb = np.zeros((32, 8, 8), dtype=int)
    qx = int(pos[0][4])
    qy = int(pos[1][4])

    qm=[]

    for L2x in range(-1,2,2):
        for L2y  in range(-1,2,2):
        # check if legal
            if 0 <= qx+L2x <= 7 and 0 <= qy+L2y <= 7:
                l2m = [qx+L2x,qy+L2y]
                qm.append(l2m)

    qc = 0

    for bb in range(0, m):  #m
        pos = GetPositions(boards[bb])
        for q in range(0,len(qm)):
            b = boards[bb].copy()
            nqx = qm[q][0]
            nqy = qm[q][1]

            if b[nqx][nqy] == 0:
                b[qx,qy] = 0
                b[nqx][nqy] = 5
                if GapExists(b):
                    ls[qc] = bb
                    qb[qc] = b
                    # print(f'board {bb} has gap with queen move {qc}')
                    qc += 1
                # else:
                #     ng[nc] = b
                #     nc += 1
                #     print(f'no gap {fc}')
                # fc += 1

    for qm in range(0,qc):
        # print(f'queen move {qm}')
        L2board = qb[qm].copy()
        pos = GetPositions(L2board)
        px = pos[0][0:4]
        py = pos[1][0:4]

        # print(px,py)
        m = 0
        for pawn in range(0,4):
            # print(f'pawn {p}')
            p = [px[pawn],py[pawn]]
            for L3 in range(-1,2,2):
                L3m = [p[0]+1,p[1]+L3]
                
                if p[0] < 7 and 0 <= p[1]+L3 <= 7:
                    if L2board[L3m[0],L3m[1]] == 0:
                        # print(f'move from {p} to {L3m}')
                        b = MakeBoard(L2board.copy(),p,L3m)
                        if not GapExists(boards[b]): 
                            if verbose:
                                print(f'solution on queen move {qm}')
                                print(b)
                            solution = b.copy()
                            break
            else:
                continue
            break
        else:
            continue
        break
    if verbose:
        print(f'qm {qm} based on board {ls[qm]}')
        print(boards[ls[qm]])
    return boards[ls[qm]]

def MakeBoard(board,p,m):
    # print(board[p[0], p[1]])
    board[int(p[0]), int(p[1])] = 0
    board[int(m[0]), int(m[1])] = 1
    return board

def CalcComputerMove_x(board, patterns, patternsq):

    this_GameState = GetGameState(board)

    nextrow = 2 if this_GameState.rows == 0 else 1

    selectedRows = board[this_GameState.minx:this_GameState.maxx+nextrow,:].copy()

    #remove queen
    queen = np.where(selectedRows == 5)
    selectedRows[queen] = 0

    #change pawn numbers to 1 - no longer needed
    # nzboard = np.nonzero(selectedRows)
    # selectedRows[nzboard] = 1

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
        legalMove = board[newPosX + this_GameState.minx, newPosY] == 0  #unoccupied

        if legalMove:

            selectedPiecePos = np.where(change == -1)
            selectedPiecePosX = int(selectedPiecePos[0][0])
            selectedPiecePosY = int(selectedPiecePos[1][0])

            selectedPiece = board[selectedPiecePosX + this_GameState.minx, selectedPiecePosY]
            board[selectedPiecePosX + this_GameState.minx, selectedPiecePosY] = 0

            board[newPosX + this_GameState.minx, newPosY] = selectedPiece   #not needed, since all pawns 1
            return board

    if verbose:
        print('Blocked, or no March pattern, using pattern q')
    #check patternsq
    nzboard = np.nonzero(board)
    #minx, maxx includes queen, so need to reselect
    minx, maxx = min(nzboard[0]), max(nzboard[0])
    sel_board = board[minx:maxx+1,:].copy()

    if verbose:
        print('sel_board')
        print(sel_board)
    pawns = np.where((sel_board > 0) & (sel_board < 5))
    # sel_board[pawns] = 1  #not needed, since all pawns 1

    pattern_match = patternsq[::2].copy()
    pattern_nextmove = patternsq[1::2,:].copy()

    foundPattern = False
    for x in range(0,pattern_match.shape[0]):
        nzboard = np.nonzero(pattern_match[x])
        pminx, pmaxx = min(nzboard[0]), max(nzboard[0])
        # print(f'minx: {minx}, maxx: {maxx}, pminx: {pminx}, pmaxx: {pmaxx}')
        match_pattern = pattern_match[x,pminx:pmaxx+1,:].copy()

        #not needed, since all pawns 1
        # pawns = np.where((match_pattern > 0) & (match_pattern < 5))
        # match_pattern[pawns] = 1

        if np.array_equal(sel_board,match_pattern):
            foundPattern = True
            if verbose:
                print(f'selected patternq: {x}')
                print(match_pattern)
            break
    
    if foundPattern:    #check if solution valid - could be at row 7
        nzboard = np.nonzero(pattern_match[x])
    # temp remove, don't recalc pminx and pmaxx
        pminx1, pmaxx1 = min(nzboard[0]), max(nzboard[0])

        # x +=1

        nzboard = np.nonzero(pattern_nextmove[x])
            # temp remove, don't recalc pminx and pmaxx
        pminx2, pmaxx2 = min(nzboard[0]), max(nzboard[0])
        # print(f'minx: {minx}, maxx: {maxx}, pminx2: {pminx2}, pmaxx2: {pmaxx2}')

        # pminx=min(pminx1,pminx2)
        # pmaxx=max(pmaxx1, pmaxx2)
        pminx, pmaxx = min(pminx1,pminx2), max(pmaxx1, pmaxx2)

        # temp remove
        sel_pattern = pattern_nextmove[x,pminx:pmaxx+1,:]
        sel_board = board[minx:minx+(pmaxx-pminx)+1,:].copy()
        # temp remove

        if verbose:
            print(f'minx: {minx}, maxx: {maxx}, pminx: {pminx}, pmaxx: {pmaxx}')
        
            print('board')
            print(sel_board)
            print('pattern')
            print(sel_pattern)

        change = sel_pattern - sel_board 

        if verbose:
            print('change')
            print(change)

        selectedPiecePos = np.where(change < 0)
        selectedPiecePosX = int(selectedPiecePos[0][0])
        selectedPiecePosY = int(selectedPiecePos[1][0])

        selectedPiece = board[selectedPiecePosX + minx, selectedPiecePosY]
        board[selectedPiecePosX + minx, selectedPiecePosY] = 0

        newPos = np.where(change > 0)
        newPosX = int(newPos[0][0])
        newPosY = int(newPos[1][0])

        board[newPosX + minx, newPosY] = selectedPiece

    else:   #No pattern
        if verbose:
            print('No pattern')

        # if GapExists(board):

        pboard = BlockGap(board)
        change = pboard - board 
        changes = np.where(change != 0)
        if len(changes[0]) > 0:
            # change = pboard - board 
            if verbose:
                print('change')
                print(change)

            selectedPiecePos = np.where(change < 0)
            selectedPiecePosX = int(selectedPiecePos[0][0])
            selectedPiecePosY = int(selectedPiecePos[1][0])

            selectedPiece = board[selectedPiecePosX, selectedPiecePosY]
            board[selectedPiecePosX, selectedPiecePosY] = 0

            newPos = np.where(change > 0)
            newPosX = int(newPos[0][0])
            newPosY = int(newPos[1][0])

            board[newPosX, newPosY] = selectedPiece

            return board
            # if len(move) > 0:

        # else:
            #move that doesn't create a gap
        board = GetNewPattern(board, sel_board, this_GameState)
        if verbose:
            print('Random move')
    # Game_on = False 
        # quit()
    return board

def BlockGap(board):
    pos = GetPositions(board)
    # print(pos)
    GotMove = False
    for p in range(0,4):
        row = int(pos[0][p])
        col = int(pos[1][p])
        # print(f'pawn {p} is at position {row}, {col}')
        # if row <= 7 and col - 1 >= 0 and board[row+1][col-1] == 0:
        if row + 1 <= 7 and col - 1 >= 0:
            if board[row+1][col-1] == 0:
                pboard = board.copy()
                pboard[row][col] = 0
                pboard[row + 1][col - 1] = 1
                if not GapExists(pboard):
                    # move = [row + 1, col - 1]
                    GotMove = True
                    break
            # print(f'\tpawn {p} can move to {row + 1}, {col - 1}') 
            # pboard = board.copy()
            # pboard[row][col] = 0
            # pboard[row + 1][col - 1] = 1
            # print(f'\tGap exists: {GapExists(pboard)}')
        # if row <= 7 and col + 1 <= 7 and board[row+1][col+1] == 0:
        if row + 1 <= 7 and col + 1 <= 7: 
            if board[row+1][col+1] == 0:
            # print(f'\tpawn {p} can move to {row + 1}, {col + 1}') 
                pboard = board.copy()
                pboard[row][col] = 0
                pboard[row + 1][col + 1] = 1
                if not GapExists(pboard):
                    # move = [row + 1, col + 1]
                    GotMove = True
                    break

    if GotMove:
        return pboard
    else:
        return board

def GapExists(board):
    pos = GetPositions(board)
    minx = int(min(pos[0]))
    newboard = CalcPossibleMoves(board)
    steps = np.where(newboard > 5)
    thru = np.where(steps[0] <= minx)
    if len(thru[0]) == 0:
        return False
    else:
        return True

def CalcPossibleMoves(board):
    qpos = np.where(board == 5)
    qposx = int(qpos[0][0])
    qposy = int(qpos[1][0])

    m = []
    loc = []
    loc.append(qposx)
    loc.append(qposy)
    m.append(loc)

    numMoves = qposx

    InclPath = False

    m1 = NextMove(board,m, False)
    m2 = NextMove(board,m1, InclPath)
    m3 = NextMove(board,m2, InclPath)
    m4 = NextMove(board,m3, InclPath)
    m5 = NextMove(board,m4, InclPath)
    m6 = NextMove(board,m5, InclPath)
    m7 = NextMove(board,m6, InclPath)

    mboard = board.copy()

    for m in m1:
        mboard[m[0],m[1]] = 6

    for m in m2:
        mboard[m[0],m[1]] = 7

    for m in m3:
        mboard[m[0],m[1]] = 8

    for m in m4:
        mboard[m[0],m[1]] = 9

    for m in m5:
        mboard[m[0],m[1]] = 10

    for m in m6:
        mboard[m[0],m[1]] = 11

    for m in m7:
        mboard[m[0],m[1]] = 12

    return mboard

def NextMove(board, m1, includeCurrent = True):

    m2 = []

    for m in m1:
    # print(m)
        m1x = m[0]
        m1y = m[1]
        # print(m1x, m1y)
        for x in range(-1,1,2):
            for y in range(-1,2,2):
                if 0 <= m1x + x <=7 and 0 <= m1y + y <=7 and board[m1x + x, m1y + y] == 0:
                    if includeCurrent:
                        
                        loc = []
                        loc.append(m1x)
                        loc.append(m1y)

                        try:
                            res = m2.index(loc)
                        except ValueError :
                            m2.append(loc)

                    loc = []
                    loc.append(m1x + x)
                    loc.append(m1y + y)

                    try:
                        res = m2.index(loc)
                    except ValueError:
                        m2.append(loc)

                    # m2.append(loc)

    return m2

def GetNewPattern(board, sel_board, this_GameState):
    #block potential winning move

    GetMove = True
    while GetMove:

        UseIndex = rand(0,3)
        LR = randTF()
        pos = GetPositions(board)
        xs = pos[0][0:4]
        ys = pos[1][0:4]

        if xs[UseIndex] < 7:
            newX = xs[UseIndex] + 1 
            newY = ys[UseIndex] + 1 if LR and ys[UseIndex] < 7 else ys[UseIndex] - 1

            if board[int(newX), int(newY)] == 0:
                GetMove = False

    board[int(xs[UseIndex]), int(ys[UseIndex])] = 0
    board[int(newX), int(newY)] = 1
    if verbose:
        print(board)

    return board

def randTF():
    return random.randint(0, 1)

def rand(min,max):
    return random.randint(min, max)

def CalcHumanMove(board):
    QPos = np.where(board == 5)
    QPosX = int(QPos[0][0])
    QPosY = int(QPos[1][0])

    possibles = []
    # print(board)
    for x in range(-1,2,2):
        for y in range(-1,2,2):
            # print(QPosX + x, QPosY + y)
            # print(board[QPosX + x, QPosY + y])
            # if board[QPosX + x, QPosY + y] == 0:
            if 0 <= QPosX + x <=7 and 0 <= QPosY + y <=7 and board[QPosX + x, QPosY + y] == 0:
                loc = []
                loc.append(QPosX + x)
                loc.append(QPosY + y)
                possibles.append(loc)

    return possibles

def SaveStart(board, filename ='start.csv'):
    # import csv
    # import numpy as np
    # example = np.zeros((2,3,4))
    backup(board)
    # num = int(array.shape[0] / 8)
    # reshaped = np.resize(array, (num,8,8))
    reshaped = np.resize(board, (1,8,8))
    reshaped = reshaped.tolist()
    # reshaped = board.tolist()
    with open(path+filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(reshaped)

def SaveThisGame(moves,move, this_game_id, Winner):
    thisdate = datetime.now().strftime('%Y%m%d')
    thistime = datetime.now().strftime('%H%M%S')
    thistimef = datetime.now().strftime('%H:%M:%S')
    
    # pg = pd.read_csv(path+'game.csv')
    # # pg = pd.DataFrame(columns=['game_id', 'queen', 'pawns', 'date', 'time', 'winner'])
    # thisdict = {'game_id': this_game_id, 'queen': 'computer', 'pawns': 'computer', 'date': thisdate, 'time': thistimef, 'winner': Winner}
    # vals = [thisdict]
    # pg = pg.append(vals)
    # pg.to_csv(path+'game.csv', index=False)


    # filename = f'int_game_{thisdate}_{thistime}.csv'
    filename = f'this_game_moves.csv'
    # dfg = pd.read_csv(path+filename)
    # print(filename)
    dfg = pd.DataFrame(columns=['game_id', 'move_id', 'position', 'squares'])
    vals = []
    save_moves = moves[0:move+1,:,:]

    # print(f'moves shape {save_moves.shape}')
    move_id = 0
    game_id = this_game_id
    for m in save_moves:
        sq = eng.GetSquares(m)
        b = bytes(sq)
        bint = int.from_bytes(b,'big')
        # thisdict = {'move_id': mc,'position': bint}
        thisdict = {'game_id': game_id, 'move_id': move_id, 'position': bint, 'squares': sq}
        # print(thisdict)
        vals.append(thisdict)

        # tb = bint.to_bytes(5,"big")
        # tbsq = []
        # for tbi in range(0,5):
        #     tbsq.append(tb[tbi])
        # print(f'{move_id} {sq} {bint} {tbsq}')
        move_id += 1

    # dfg = dfg.concat(vals)
    # dfg = dfg.append(vals)

    # dfg = pd.concat([dfg, pd.DataFrame.from_records([vals])])
    dfg = pd.DataFrame(vals, columns = ['game_id','move_id','position','squares'])
    currdir = os.getcwd()
    dfg.to_csv(currdir+'\\'+filename, index=False)
    # dfg.to_csv(path+filename, index=False)

def SaveGame(moves,move, this_game_id, Winner):
    thisdate = datetime.now().strftime('%Y%m%d')
    thistime = datetime.now().strftime('%H%M%S')
    thistimef = datetime.now().strftime('%H:%M:%S')
    
    pg = pd.read_csv(path+'game.csv')
    # pg = pd.DataFrame(columns=['game_id', 'queen', 'pawns', 'date', 'time', 'winner'])
    thisdict = {'game_id': this_game_id, 'queen': 'computer', 'pawns': 'computer', 'date': thisdate, 'time': thistimef, 'winner': Winner}
    vals = [thisdict]
    pg = pg.append(vals)
    pg.to_csv(path+'game.csv', index=False)


    # filename = f'int_game_{thisdate}_{thistime}.csv'
    filename = f'game_moves.csv'
    dfg = pd.read_csv(path+filename)
    # print(filename)
    # dfg = pd.DataFrame(columns=['game_id', 'move_id', 'position'])
    vals = []
    save_moves = moves[0:move+1,:,:]

    # print(f'moves shape {save_moves.shape}')
    move_id = 0
    game_id = this_game_id
    for m in save_moves:
        sq = eng.GetSquares(m)
        b = bytes(sq)
        bint = int.from_bytes(b,'big')
        # thisdict = {'move_id': mc,'position': bint}
        thisdict = {'game_id': game_id, 'move_id': move_id, 'position': bint, 'squares': sq}
        # print(thisdict)
        vals.append(thisdict)
        tb = bint.to_bytes(5,"big")
        tbsq = []
        for tbi in range(0,5):
            tbsq.append(tb[tbi])
        # print(f'{move_id} {sq} {bint} {tbsq}')
        move_id += 1
    dfg = dfg.append(vals)
    # dfg.to_csv(path+filename, index=False)
    currdir = os.getcwd()
    dfg.to_csv(currdir+'\\'+filename, index=False)
    # b = bytes(sq)
    #             # print(b)
    # bint = int.from_bytes(b,'big')
    # # print(id, game_id, move_id, bint)
    # thisdict = {'position': bint}
    # # thisdict = {'game_id': game_id, 'move_id': move_id, 'position': bint}

    # print(thisdict)

    # save_moves = moves[0:move,:,:]
    # reshaped = np.resize(save_moves, (move,8,8))
    # reshaped = reshaped.tolist()
    # # reshaped = board.tolist()
    # with open(path+filename, 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile, delimiter=',')
    #     writer.writerows(reshaped)

def xSaveGame(moves,move):
    # import csv
    # import numpy as np
    # example = np.zeros((2,3,4))
    # backup(board)
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'game_{date}.csv'

    print(filename)
    # num = int(array.shape[0] / 8)
    # reshaped = np.resize(array, (num,8,8))
    save_moves = moves[0:move,:,:]
    reshaped = np.resize(save_moves, (move,8,8))
    reshaped = reshaped.tolist()
    # reshaped = board.tolist()
    with open(path+filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerows(reshaped)

def backup(boards_to_write):

    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'start_{date}.csv'

    if verbose:
        print(filename)

    num = int(boards_to_write.shape[0] / 8)
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
    # print(f'minx: {minx}, maxx: {maxx}')
    gap = qposx - maxx

    if verbose:
        print(f'qx: {qposx}, qy: {qposy}, gap: {gap}')

    this_GameState = GameState(xs, ys, minx, maxx, qposx, qposy, rows, gap)

    return this_GameState

def GetPositions(board):

    pos = np.empty([2,5], dtype=int)
    
    # for p in range(1,5):    
    #     r = np.where(board == p)
    #     pos[0,p-1] = int(r[0][0])
    #     pos[1,p-1] = int(r[1][0])

    rs = np.where((0 < board) & (board < 5))
    for p in range(0,4):
        # print(rs[0][p], rs[1][p])
        pos[0,p] = int(rs[0][p])
        pos[1,p] = int(rs[1][p])

    # rs = np.where(board == 1)
    # p = 0
    # for r in rs:
    #     pos[0,p] = int(r[0][0])
    #     pos[1,p] = int(r[1][0])
    #     p += 1

    qpos = np.where(board == 5)
    pos[0,4] = int(qpos[0][0])
    pos[1,4] = int(qpos[1][0])

    return(pos)

def CreateBasicPatterns():
    rows = 2
    cols = 8
    aboard = np.zeros((10, rows, cols), dtype=int)

    board = CreateNewBoard(0, rows, cols)
    bcounter = 0
    aboard[bcounter] = board
    bcounter += 1

    for y in range(0,board.shape[1],2):
        board[0,y] = 0
        board[1,y+1] = 1
        aboard[bcounter] = board
        bcounter += 1

    board = CreateNewBoard(1, rows, cols)
    aboard[bcounter] = board
    bcounter += 1

    # for x in range(1,board.shape[1],2):
    for y in range(board.shape[1]-1,0,-2):
        board[0,y] = 0
        board[1,y-1] = 1
        aboard[bcounter] = board
        bcounter += 1

    return aboard

def CreateNewBoard(start = 0, rows = 8, cols = 8):
    board = np.zeros((rows, cols), dtype=int)

    for c in range(start,cols,2):
        # print(x)
        board[0,c] = 1

    return board

def March_x(board,samerow, xs, ys):
    if samerow:
        if np.min(xs) == 0: #left border
            lbi = np.argmin(xs)
            #piece at x = 0, y = ys[lbi]
            lb_y = int(ys[np.argmin(xs)])
            piece = board[0,lb_y]
            board[0,lb_y] = 0
            board[1, lb_y + 1] = piece
        if np.max(xs) == 7: #right border
            lbi = np.argmax(xs)
            #piece at x = 0, y = ys[lbi]
            lb_y = int(ys[np.argmax(xs)])
            piece = board[7,lb_y]
            board[7,lb_y] = 0
            board[6, lb_y + 1] = piece
    else:
        rows = np.max(ys) - np.min(ys)

    return board



def DrawScreen(screen, board, myfont, Queen_Move, prevb):

    save_board = board.copy()

    if np.array_equal(board,prevb): 
        if verbose:
            print('no change')

    # pos = GetPositions(board)
    # # print(pos)
    # minx = int(min(pos[0][0:4]))
    # qx = int(pos[0][4:5])
    # qy = int(pos[1][4:5])
    # if qx <= minx:  #player wins
    #     pygame.display.set_caption(f'Game over - you win')
    #     # pygame.draw.rect(screen, 'Yellow', [qy*squaresize, qx*squaresize, rectsize, rectsize], 2)
    #     # pygame.display.flip()
    #     return False

        # Game_on = DrawsSreen(screen, board, myfont)

    # print('DrawScreen')
    Possibles = CalcHumanMove(board)
    PossibleMoves = np.asarray(Possibles)

    xboard = board.transpose()

    if not Queen_Move:
        cb = board - prevb
        cbx = cb.transpose()
        # print(cbx)
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
            # print(xpos,ypos)
            pygame.draw.rect(screen, colour, [xpos*squaresize, ypos*squaresize, rectsize, rectsize], 2)

    pos = GetPositions(board)
    # print(pos)
    minx = int(min(pos[0][0:4]))
    # qx = int(pos[0][4:5])
    # qy = int(pos[1][4:5])
    qx = int(pos[0][4])
    qy = int(pos[1][4])

    if qx <= minx:  #player wins
        pygame.display.set_caption(f'Game over - you win')
        # pygame.draw.rect(screen, 'Yellow', [qy*squaresize, qx*squaresize, rectsize, rectsize], 2)
        # pygame.display.flip()
        return False

    pygame.display.flip()

    # time.sleep(2)

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
            nwrow = []
            for r in row:
                # nwrow.append(eval(r))
                board_csv.append(eval(r))
            # board_csv.append(nwrow)
        board = np.asarray(board_csv)

        if verbose:
            print(board)

    else:
    
        p = 1
        for col in range(0,squares,2):
            # board[0,col] = p
            board[0,col] = 1
            p+= 1

        row, col = 7,3
        board[row,col] = 5

        if verbose:
            print(board)

    return board

def LoadPatterns(filename):

    with open(thisdir+'\\files\\'+filename, 'r') as f:
    # with open(path+filename, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # print(examples)
    patterns = []
    for row in rows:
        nwrow = []
        for r in row:
            nwrow.append(eval(r))
        patterns.append(nwrow)
    # print(nwexamples)

    return patterns

# ipatterns = Load_I_Patterns('iboards.csv')
# cmboard = eng.LoadStart()
# tboard = PatternMatchMove(cmboard,ipatterns)

try:
    # for g in range(500,1000):
    #     print(f'game {g}')
    KeepPlaying = True
    while KeepPlaying:
        KeepPlaying = mainx(0)
    # print('Game over')
except:
    # print(save_board)
    # SaveGame(moves, move)
    # print()
    print("Error!", sys.exc_info()[0], "occurred.")
    import traceback
    traceback.print_exc()
    # sys.traceback.print_exc()
