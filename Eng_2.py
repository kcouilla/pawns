import pandas as pd
import numpy as np
import time
from random import randrange
import os as os
import sys
import pathlib
from pathlib import Path

td = os.getcwd()
# pg = pd.read_csv(td+'\\files\\game.csv')

# DB_path = Path('C:/Users/kcoui/source/repos/Budget/Budget.db')
path='C:\\Users\\kcoui\\source\\repos\\Python\\pawns\\files\\'
codepath = 'C:\\Users\\kcoui\\source\\repos\\Python\\pawns\\'

thisdir = os.getcwd()
print(thisdir)

import csv

# sys.path.insert(0, codepath)
sys.path.insert(0, thisdir + '\\')
# cpath = os.path.join(codepath, 'basic_stuff')
import basic_stuff as bs

# pg = pd.read_csv(path+'game.csv')
# dfg = pd.read_csv(path+'game_moves.csv')

# filedir = Path.cwd() / 'files' 
pg = pd.read_csv(Path.cwd() / 'files' / 'game.csv')
dfg = pd.read_csv(Path.cwd() / 'files' / 'game_moves.csv')

# pg = pd.read_csv(thisdir+'\\files\\game.csv')
# dfg = pd.read_csv(thisdir+'\\files\\game_moves.csv')

pgPawnWins = pg[pg['winner']=='Pawns']
pgQueenWins = pg[pg['winner']=='Queen']

pgPawn = pd.merge(pgPawnWins, dfg, on="game_id")
pgQueen = pd.merge(pgQueenWins, dfg, on="game_id")

verbose = False
Include_KQ_Bug = True
Difficulty = 1.5

def Square(row, col):
    square = int((row * 4) + ((col + 1) /2) + .5)

    return square

def GetSquares(sboard):
    pos = GetPositions(sboard)
    # print(pos)
        # iboard = [0, -1]
    xboard = []
    for i in range(0,len(pos[1])):
        xboard.append(Square(pos[0,i], pos[1,i]))    

    return xboard

def MakeInt(board):
    sq = GetSquares(board)
    sqint = [int(i) for i in sq]
    b = bytes(sqint)
    bint = int.from_bytes(b,'big')
    return bint

def FindBoard(lineage, sboard):
    sq = GetSquares(sboard)
    # print(sq)
    for l in lineage:
        allpos = [l[6], l[7], l[8], l[9], l[10]]
        if allpos == sq:
            break
        # print(l)
    return l

def MakeBigInt(board):

    sq = GetAllSquares(board)
    # print(sq)
    # if pawns:
    sq = sq[0:7]
    # print(sq)

    sqint = [int(i) for i in sq]
    b = bytes(sqint)
    bint = int.from_bytes(b,'big')

    return bint

def GetAllSquares(sboard):
    # pos = GetAllPositions(sboard)
    pos = GetPositions(sboard)
    # print(pos)
        # iboard = [0, -1]
    xboard = []
    for i in range(0,len(pos[1])):
        xboard.append(Square(pos[0,i], pos[1,i]))    

    return xboard

def GetRowCol(position):
    cpr = int((position-.5)/4)
    cpc = int((2 * (position - (cpr * 4))) - 2)
    cpc = cpc + 1 if (cpr % 2) == 1 else cpc
    return [cpr, cpc]

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

def MakeBoardFromPosition(position):
    board = np.zeros((8, 8), dtype=int)
    tb = position.to_bytes(5,"big")
    tbsq = []
    for tbi in range(0,4):
        tbsq.append(tb[tbi])
        rc = GetRowCol(tb[tbi])
        board[rc[0],rc[1]] = 1

    rc = GetRowCol(tb[4])
    tbsq.append(tb[4])
    board[rc[0],rc[1]] = 5

    return board

def MakeBoardFromInt(position):
    board = np.zeros((8, 8), dtype=int)

    tb = position.to_bytes(5,"big")
    # print(tb,len(tb))
    tbsq = []
    for tbi in range(0,len(tb)):
        tbsq.append(tb[tbi])
        rc = GetRowCol(tb[tbi])
        # bval = 2
        if tbi <= 3:
            bval = 1
        else:
        # if tbi == 3:
            bval = 5

        board[rc[0],rc[1]] = bval

    # print(tbsq)

    return board

def LoadStart(fname='start.csv'):

    board = np.zeros((8, 8), dtype=int)

    # if LoadStart:
    # with open(path+'start_02_28_1.csv', 'r') as f:
    with open(path+fname, 'r') as f:
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

    # print(board)

    pos = GetPositions(board)
    # iboard = [0, -1]
    xboard = []
    for i in range(0,len(pos[1])):
        xboard.append(Square(pos[0,i], pos[1,i]))
        # print(pos[0,i], pos[1,i], Square(pos[0,i], pos[1,i]))
        # print(Square(pos[0,i], pos[1,i]))

    # print(board)

    nboard = {"p1": xboard[0], "p2": xboard[1], "p3": xboard[2], "p4": xboard[3], "q": xboard[4], "id": -1, "gen": 0, "parent": -1, "gap": 0}
    # print(iboard)
    # return nboard
    return board

def PawnMoves(board):

    # print('PawnMoves')

    # MoveStatus = np.ones((8, 1), dtype=int)
    boards = np.zeros((8, 8, 8), dtype=np.int8)

    pos = bs.GetPositions(board)
    px = pos[0][0:4]
    py = pos[1][0:4]

    # print(px,py)
    m = 0
    for pawn in range(0,4):
        
        p = [px[pawn],py[pawn]]
        for l1 in range(-1,2,2):
            # p = [px,py]
            # l1m = [px+1,py+l1]
            l1m = [p[0]+1,p[1]+l1]
            
            if p[0] < 7 and 0 <= p[1]+l1 <= 7:
                if board[l1m[0],l1m[1]] == 0:
                    b = bs.MakeBoard(board.copy(),p,l1m)

                    # if not isKillerQueen(b)[0]:
                    #     boards[m] = b
                    #     m += 1

                    boards[m] = b
                    m += 1

    retBoards = np.resize(boards,(m,8,8))

    # return boards
    return retBoards

def QueenMoves(board):

    boards = np.zeros((4, 8, 8), dtype=np.int8)

    pos = bs.GetPositions(board)
    
    qx = int(pos[0][4])
    qy = int(pos[1][4])
    
    # print(qx,qy)
    qm=[]
    qc = 0
    for l2x in range(-1,2,2):
        for l2y  in range(-1,2,2):
        # check if legal
            if 0 <= qx+l2x <= 7 and 0 <= qy+l2y <= 7:
                l2m = [qx+l2x,qy+l2y]
                qm.append(l2m)

    for q in range(0,len(qm)):  #4 possible queen moves
        b = board.copy()
        nqx = qm[q][0]  # new queen x
        nqy = qm[q][1]  # new queen y
        #move queen 
        if b[nqx][nqy] == 0:    # if cell not occupied
            b[qx,qy] = 0
            b[nqx][nqy] = 5
            boards[qc] = b
            qc += 1
            # pos = bs.GetPositions(b)
            # print(f'board after queen move {q}')
            # ShowBoard(b)

    retBoards = np.resize(boards,(qc,8,8))

    return retBoards

def CalcEscapeRoutes(cboard):

# cboard = cmboard.copy()
# bs.ShowBoard(cboard)

    qpos = np.where(cboard == 5)
    ppos = np.where(cboard == 1)

    qposx = int(qpos[0][0])
    qposy = int(qpos[1][0])

    ppx = ppos[0]
    ppy = ppos[1]
    minx = min(ppx)

    r1 = [] # moves to check
    r1c = 0 # counter for r1

    r1.append([qposx, qposy])

    mboard = cboard.copy()
    npos = np.where(mboard == 5)

    nqx = npos[0]
    if len(nqx) == 0:
        minnqx = 0
    else:
        minnqx = min(nqx)

    while len(r1) > r1c:    # and minnqx > minx:
        nextpos = r1[r1c]
        thisval = mboard[nextpos[0],nextpos[1]]
        nextval = thisval if thisval != 5 else 50
        m1 = bs.NextMove(cboard, [nextpos], False)

        # if len(m1) > 0:
        #     if m1[0][0] == 0:   #row 0, done if can reach
        #         break

        for m in m1:
            if mboard[m[0],m[1]] == 0 and m not in r1:
                mboard[m[0],m[1]] = nextval + 5
                r1.append(m)

            if m1[0][0] == 0:   #row 0, done if can reach
                break

        npos = np.where(mboard > 5)
        nqx = npos[0]
        if len(nqx) == 0:
            minnqx = 0
        else:
            minnqx = min(nqx)

        r1c += 1
        
    return mboard

def CanEscape(ceboard):
    tboard = CalcEscapeRoutes(ceboard)

    # endrow = np.where(tboard == np.max(tboard))[0][0]

    trow = np.where(tboard > 50)  #[0][0]

    if len(trow[0]) > 0:
        
        endrow = min(trow[0])

        ppos = np.where(tboard == 1)
        ppx = ppos[0]
        ppy = ppos[1]
        minx = min(ppx)

        if endrow <= minx:
            EscapeRoute = 1
        else:
            EscapeRoute = 0
    else:
        EscapeRoute = 0

    return EscapeRoute

def CalcPath(lineage, thisid):
    parent = lineage[thisid][2]
    route = []
    route.append(thisid)

    while parent > -1:
        thisid = parent
        route.append(thisid)
        parent = lineage[thisid][2]

    route.reverse()
    return route

def CalcMetrics(mboard, mlineage):
    arr = np.array(mboard)
    # arrK = CalcEscapeRoutes(arr)
    # arrK = CalcEscapeRoutes(arr)
    arrK = CriticalPath(arr)
    startrow = np.where(arrK == 5)[0]
    # print(startrow)

    pathboard = arrK[np.where(arrK  > 5)]
    endrow = np.where(arrK == np.max(arrK))[0][0]

    # print(f'startrow {startrow}, len {len(startrow)}, endrow {endrow}')

    if len(startrow) == 0:
        # bs.ShowBoard(mboard)
        # bs.ShowBoard(arrK)
        startrow_val = 0
    else:
        startrow_val = startrow[0]

    rg = startrow_val - endrow

    if len(pathboard) > 0:
        moves = int((np.max(pathboard) - 50)  / 5)
    else:
        moves = 0

    mlineage[3] = CanEscape(arrK)
    mlineage[4] = rg
    mlineage[5] = moves

    # print(mlineage)

    return mlineage

def MakeBoard(mblineage):

    # for l in lineage[p]:
    # print(f'MakeBoard {mblineage}')

    # for l in lineage[p]:
    # print(l)
    mbboard = np.zeros((8, 8), dtype=np.int8)
    for s in mblineage[6:10]:
        rc = GetRowCol(s)
        mbboard[rc[0], rc[1]] = 1
    
    rc = GetRowCol(mblineage[10])
    mbboard[rc[0], rc[1]] = 5

    return mbboard
        # bs.ShowBoard(board)
    
def QueenPawn(qplineage):
    # queen move
    NextId = len(qplineage)
    gen = max(qplineage[:,0])

    # print(f'gen {gen} NextId {NextId}')

    ThisRound = qplineage[qplineage[:,0] == gen]

    gen += 1

    GotWinner, GotStopper, GotMove = False, False, False

    for x in ThisRound: 
        id = x[1]
        ParentMoves = x[5]
        # print(f'ParentMoves {ParentMoves}')
        bo = MakeBoard(x)
        qm = QueenMoves(bo)

        qmc = len(qm)       #count of new queen moves

        if gen == 2:

        ### check if no queen moves - trapped! ###
            if qmc == 0:
                if verbose:
                    print(f'Winner: move {id} has {qmc} children')
                # bs.ShowBoard(Keepers[p])    
                BestMove = id
                GotMove = True
                qplineage[id,11] = 2
                # break

            ### check if paths blocked
            if x[3] == 0 and not GotMove:
                if verbose:
                    print(f'Stopper: move {id} has no escape path')
                # bs.ShowBoard(Keepers[p])    
                BestMove = id
                GotMove = True
                qplineage[id,11] = 1
                # break
        ###########################################

        # GotMove = GotWinner or GotStopper

        if not GotMove:

            if len(qm) > 0:
                
                for q in qm:

                    lineage_temp = np.zeros((1,12), dtype=int)

                    lineage_temp[0,0] = gen     #generation
                    lineage_temp[0,1] = NextId  #id
                    lineage_temp[0,2] = id     #parent
                    lineage_temp[0] = CalcMetrics(q, lineage_temp[0])

                    squares = GetSquares(q)
                    for s in range(0,5):
                        lineage_temp[0,s+6] = squares[s]

                    lineage_temp[0,11] = 0

                    # if lineage_temp[0,3] == 0:
                    #     lineage_temp[0,11] = 1

                    ChildMoves = lineage_temp[0,5]

                    if 1 == 1:
                        qplineage = np.append(qplineage, lineage_temp, axis = 0) 
                        NextId += 1
                        # Keepers.append(q)

    # pawn move
    if not GotMove:    
        ThisRound = qplineage[qplineage[:,0] == gen]

        gen = gen + 1 

        for x in ThisRound: 
            id = x[1]   #id of parent queen
            # print(f'queen id {id}')
            bo = MakeBoard(x)
            pm = PawnMoves(bo)
            if len(pm) > 0:
                qplineage = np.resize(qplineage,(NextId + len(pm),12))   
                
                for p in pm:
                    qplineage[NextId,0] = gen     #generation
                    qplineage[NextId,1] = NextId  #id
                    qplineage[NextId,2] = id     #parent
                    qplineage[NextId] = CalcMetrics(p, qplineage[NextId])

                    squares = GetSquares(p)
                    for s in range(0,5):
                        qplineage[NextId,s+6] = squares[s]

                    qm = QueenMoves(p)
                    # print(f'id {NextId} has {qm.shape[0]} possible queen moves')

                    if qm.shape[0] == 0:
                        qplineage[NextId,11] = 2
                    else:
                        qplineage[NextId,11] = 0

                    # if qplineage[NextId,3] == 0:
                    #     qplineage[NextId,11] = 1

                    NextId += 1

    return qplineage

def CriticalPath(cmboard):

    CritPath = CriticalPathList(cmboard)

    CritPath.reverse()

    cpboard = cmboard.copy()

    # print(CritPath)
    em = 55
    for c in CritPath:
        cpboard[c[0],c[1]] = em
        em += 5

    return cpboard


# def CriticalPath(cmboard):

#     # fix for multiple

#     cpboard = CalcEscapeRoutes(cmboard)

#     CritPath = []
#     em = np.max(cpboard)

#     empos = np.where(cpboard == em)
#     emrow = empos[0][0]
#     emcol = empos[1][0]

#     CritPath.append([emrow, emcol])

#     emincr = -10

#     rowincr = 1

#     while em > 50 and emrow < 8:  # and em not in fixed:
#         empos = np.where(cpboard[emrow] == em)

#         if len(empos[0]) == 0:
#             rowincr = rowincr * -1
#             emrow += rowincr
#         else:
#             scol = [emcol + 1, emcol - 1]
#             for e in empos[0]:
#                 if e in scol:
#                     CritPath.append([emrow, e])

#             emcol = empos[0][0]
#             em += emincr
        
#         emrow += rowincr

#     em = np.max(cpboard)
#     r = CritPath[0][0]

#     cpboard = cmboard.copy()

#     for c in CritPath:
#         if c[0] != r:
#             em -= 10
#             r = c[0]

#         cpboard[c[0],c[1]] = em
        
#     return cpboard

def CriticalPathList(cmboard):

    cpboard = CalcEscapeRoutes(cmboard)
    # bs.ShowBoard(cpboard)
    # print()

    CritPath = []
    em = np.max(cpboard)

    empos = np.where(cpboard > 50)

    if 0 in empos[0]:   #escape path reaches row 0
        r0 = cpboard[0,:]
        # em = min(r0[np.where(r0 != 0)]) # get min value on row 0
        em = min(r0[np.where(r0 > 1)]) # get min value on row 0
    else:
        em = np.max(cpboard)

    empos = np.where(cpboard == em)
    emrow = empos[0][0]
    emcol = empos[1][0]

    lookupRow = emrow
    lookupCol = emcol

    # CritPath.append([emrow, emcol])

    # print(CritPath)

    # find less than and neighbouring

    em -= 5

    while em > 50:

        empos = np.where(cpboard == em)
        xpos = empos[0]
        ypos = empos[1]

        # print(empos)
        for e in range(0,len(xpos)):
            if xpos[e] in [lookupRow+1, lookupRow-1] and ypos[e] in [lookupCol+1, lookupCol-1]:
                # print(f'{xpos[e]}, {ypos[e]} might be a neighbour')
                lookupRow = xpos[e]
                lookupCol = ypos[e]
                CritPath.append([lookupRow, lookupCol])
        em -= 5
            
    # oldpath = CriticalPathList(cmboard)
    # print(oldpath)
    # print('new path')

    # print(CritPath)

    return CritPath

def CriticalPathListSquares(cmboard):

    cpboard = CalcEscapeRoutes(cmboard)
    # bs.ShowBoard(cpboard)
    # print()

    CritPath = []
    em = np.max(cpboard)

    empos = np.where(cpboard > 50)

    if 0 in empos[0]:   #escape path reaches row 0
        r0 = cpboard[0,:]
        em = min(r0[np.where(r0 != 0)]) # get min value on row 0
    else:
        em = np.max(cpboard)

    empos = np.where(cpboard == em)
    emrow = empos[0][0]
    emcol = empos[1][0]

    lookupRow = emrow
    lookupCol = emcol

    CritPath.append(Square(emrow, emcol))
    # CritPath.append([emrow, emcol])

    # print(CritPath)

    # find less than and neighbouring

    em -= 5

    while em > 50:

        empos = np.where(cpboard == em)
        xpos = empos[0]
        ypos = empos[1]

        # print(empos)
        for e in range(0,len(xpos)):
            if xpos[e] in [lookupRow+1, lookupRow-1] and ypos[e] in [lookupCol+1, lookupCol-1]:
                # print(f'{xpos[e]}, {ypos[e]} might be a neighbour')
                lookupRow = xpos[e]
                lookupCol = ypos[e]
                # CritPath.append([lookupRow, lookupCol])
                CritPath.append(Square(lookupRow, lookupCol))
        em -= 5
            
    # oldpath = CriticalPathList(cmboard)
    # print(oldpath)
    # print('new path')

    # print(CritPath)

    return CritPath

def CriticalPathListMulti(cmboard):

    cpboard = CalcEscapeRoutes(cmboard)

    CritPaths = []

    em = np.max(cpboard)

    empos = np.where(cpboard == em)
    emrow = empos[0][0]
    emcol = empos[1][0]

    xs = empos[0]
    ys = empos[1]

    for ems in range(0,len(xs)):

        emrow = xs[ems]
        emcol = ys[ems]

        em = cpboard[emrow, emcol]

        lookupRow = emrow
        lookupCol = emcol

        CritPath = [[lookupRow,lookupCol]]

        em -= 5

        while em > 50:

            empos = np.where(cpboard == em)
            xpos = empos[0]
            ypos = empos[1]

            for e in range(0,len(xpos)):
                if xpos[e] in [lookupRow+1, lookupRow-1] and ypos[e] in [lookupCol+1, lookupCol-1]:
                    lookupRow = xpos[e]
                    lookupCol = ypos[e]
                    CritPath.append([lookupRow, lookupCol])
            em -= 5

        if CritPath not in CritPaths:
            CritPaths.append(CritPath)
            
    return CritPaths

def BlockersList(blboard):

    pos = bs.GetPositions(blboard)
    px = pos[0][0:4]
    py = pos[1][0:4]

    # minx = min(px)

    m = 0
    reach = []
    r1 = []
    for pawn in range(0,4):
        r1.append([px[pawn], py[pawn]])

        while len(r1) > m:
        
            nextpos = r1[m]

            fx = nextpos[0] + 1
            fy = nextpos[1] - 1

            if fx < 8 and 0 <= fy <= 7 and blboard[fx, fy] == 0:
                newpos = [fx, fy]
                if newpos not in r1:
                    r1.append(newpos)

            fy += 2
            if fx < 8 and 0 <= fy <= 7 and blboard[fx, fy] == 0:
                newpos = [fx, fy]
                if newpos not in r1:
                    r1.append(newpos)

            m += 1

    return r1

def GetPawnPositionsList(pboard):

    p = GetPositions(pboard)
    # print(p)
    pos = []
    for ps in range(0,len(p[0]) - 1):
        pos.append([p[0,ps],p[1,ps]])

    return pos

def PawnOneMoveList(blboard):

    pos = bs.GetPositions(blboard)
    px = pos[0][0:4]
    py = pos[1][0:4]

    reach = []
    r1 = []
    numMoves = 1

    for pawn in range(0,4):
        nextpos = [px[pawn], py[pawn]]

        fx = nextpos[0] + 1
        fy = nextpos[1] - 1

        if fx < 8 and 0 <= fy <= 7 and blboard[fx, fy] == 0:
            newpos = [fx, fy]
            if newpos not in r1:
                r1.append(newpos)

        fy += 2
        if fx < 8 and 0 <= fy <= 7 and blboard[fx, fy] == 0:
            newpos = [fx, fy]
            if newpos not in r1:
                r1.append(newpos)

    return r1

def CalcLineage(cmboard):
    tlineage = np.zeros((12), dtype=int)
    tlineage[0] = -1   #generation
    tlineage[1] = -1    #id
    tlineage[2] = -1   #parent
    tlineage = CalcMetrics(cmboard, tlineage)

    squares = GetSquares(cmboard)

    for s in range(0,5):
        tlineage[s+6] = squares[s]
    # print(tlineage)
    return tlineage

def IsHat(pml):
    possMoves = pml[6:11]
    # qrow1 = GetRowCol(pml[10])
    # qrow = qrow1[0]
    minrow = GetRowCol(pml[6])[0]
    # print(qrow)
    hat = False
    if (minrow % 2) == 0: #even row
        gap1 = -3
        gap2 = -4
    else:
        gap1 = -4
        gap2 = -5
    # 0 compared with 1 and 2
    if possMoves[0] - possMoves[1] == gap1 and possMoves[0] - possMoves[2] == gap2: # and possMoves[0] - possMoves[4] == -8:
        hat = True
    # 0 compared with 2 and 3
    if possMoves[0] - possMoves[2] == gap1 and possMoves[0] - possMoves[3] == gap2:  # and possMoves[0] - possMoves[4] == -8:
        hat = True
    # 0 compared with 2 and 3
    if possMoves[1] - possMoves[2] == gap1 and possMoves[1] - possMoves[3] == gap2: # and possMoves[1] - possMoves[4] == -8:
        hat = True

    return hat

def isKillerQueen(kq):
    qm = QueenMoves(kq)
    qmc = 0
    KillerQueen = False
    for q in qm:
        qcpl = CriticalPathList(q)
        if len(qcpl) == 0 or qcpl[0][0] > 1:
            return [False, kq]
        CanBlock = False
        pm = PawnMoves(q)
        pmc = 0    
        for p in pm:
            ppos = GetPawnPositionsList(p)
            for pp in ppos:
                if pp in qcpl:
                    CanBlock = True
            pmc += 1
        if not CanBlock:
            KillerQueen = True
            kq = q.copy()
            # print('Killer Queen')
        qmc += 1
    return [KillerQueen,kq]

def CalcMove(cmboard):
    GotSolution = 'Not yet'
    SolutionLevel = 0

    GotWinner = False
    GotStopper = False
    GotMove = GotStopper or GotWinner
    BestMove = -1

    sq = GetSquares(cmboard)
    sqint = [int(i) for i in sq]

    b = bytes(sqint)
    bint = int.from_bytes(b,'big')

    # print(f'position is {bint} from {sqint}')

    if verbose:
        print(f'position is {bint} from {sqint}')
        bs.ShowBoard(cmboard)

    res = Analysis1(cmboard)
    print('Analysis1')

    if verbose:
        print(res[3])

    if res[0]:
        return res[1]
    else:
        if Difficulty >= 1.5:
            res = Analysis1_A(cmboard, res[2])   # res2 is lineage
        else:
             return MoveMostDistant(cmboard)
        print('Analysis1_A')

    if verbose:
        print(res[3])

    if res[0]:
        return res[1]
    else:
        if Difficulty >= 2:
        # if 1 == 1:
            res = Analysis2(cmboard, res[2])   # res2 is lineage
        else:
            return MoveMostDistant(cmboard)
        print('Analysis2')

    if res[0]:
        if verbose:
            print(res[3])
        return res[1]
    else:
        # if Difficulty >= 3:
        if 1 == 1:
            res = Analysis3(cmboard, res[2]) 
        else:
            return res[1]
        print('Analysis3')

    if res[0]:
        if verbose:
            print(res[3])
        return res[1]
    else:
        # if Difficulty == 4:
        if 1 == 1:
            res = Analysis4(cmboard, res[2]) 
        else:
            return res[1]
        print('Analysis4')

    if res[0]:
        if verbose:
            print(res[3])
        return res[1]
    else:
        if verbose:
            print('no solution')
        print('no solution')
        return cmboard
    
def calculate_distances(pos):
    rows = pos[0]
    cols = pos[1]
    
    row5, col5 = rows[4], cols[4]
    
    distances = []
    for i in range(4):
        row, col = rows[i], cols[i]
        distance = np.sqrt((row5 - row)**2 + (col5 - col)**2)
        distances.append(distance)
    
    return distances
    
def MoveMostDistant(board):
    print('MoveMostDistant')
    pos = GetPositions(board)

    distances = calculate_distances(pos)
    # print(f'distances: {distances}')
    indices_sorted_by_distance = np.argsort(distances)[::-1]  # Indices of pieces sorted by distance (most distant first)
    # print(f'largest distance index: {indices_sorted_by_distance[0]}')
    prev_row, prev_col = pos[0][indices_sorted_by_distance[0]], pos[0][indices_sorted_by_distance[1]]
    # print(f'largest distance position: {prev_row}, {prev_col}')

    occupied_positions = set(zip(pos[0], pos[1]))
    q_row, q_col = pos[0][4], pos[1][4]

    sel_piece, sel_move, sel_change, dist_change = -1, -1, 999, 0

    for index in indices_sorted_by_distance:
        rowi, coli = pos[0][index], pos[1][index]
        possible_moves = [
            (rowi + 1, coli + 1),
            (rowi + 1, coli - 1)]
        for p in possible_moves:
            if p not in occupied_positions:
                row, col = p[0],p[1]
                distance = np.sqrt((q_row - row)**2 + (q_col - col)**2)
                dist_change = distance - distances[index]
                if dist_change < sel_change:
                    sel_change, sel_piece, sel_move = dist_change, index, p

    # print(f'sel_change {sel_change}, sel_piece {sel_piece}, sel_move {sel_move}')

    prev_row, prev_col = pos[0][sel_piece], pos[1][sel_piece]

    board[prev_row, prev_col] = 0
    board[sel_move[0], sel_move[1]] = 1

    return board


def Analysis1(cmboard):

    res = []
    GotMove = False
    
    GoodMoves = []

    # print('before')

    pm1 = PawnMoves(cmboard)

    pm = pm1.copy()

    # pm = np.zeros((8, 8, 8), dtype=np.int8)

    # pc = 0
    # for p in pm1:
    #     if not isKillerQueen(p)[0]:
    #         # pm.append(p)
    #         pm[pc] = p
    #         pc += 1

    # pm = np.resize(pm,(pc,8,8))

    # print('after')

    npm = len(pm)

    lineage = np.zeros((npm, 12), dtype=int)

    ###########################################
    # if 0 or 1 pawn moves possible, end analysis
    ##########################################

    if npm == 0:
        res.append(True)
        res.append(cmboard.copy())
        res.append(lineage)
        res.append('No moves possible')
        return res

    if npm == 1:
        res.append(True)
        res.append(pm[0,:])
        res.append(lineage)
        res.append('One move possible')
        return res

    #############################################
    # check for killer queen - forced move
    #############################################
    
    if Include_KQ_Bug:
    
        kq = isKillerQueen(cmboard)
        if kq[0]:
            if verbose:
                print(f'is killer')
                bs.ShowBoard(kq[1])
            pos = GetPositions(kq[1])
            # pos = eng.GetPositions(kq[1])
            qpos = [pos[0,4],pos[1,4]] 
            if verbose:
                print(f'must block {qpos}')

            pmkq = PawnMoves(cmboard)
            for p in pmkq:
                ppos = GetPawnPositionsList(p)
                for pp in ppos:
                    # print(f'can {pp} block {qpos}?')
                    if pp == qpos:
                        # print('got blocker')
                        # bs.ShowBoard(p)

                        res.append(True)
                        res.append(p)
                        res.append(lineage)
                        res.append('Killer Queen blocker')
                        if verbose:
                            print('Blocking Killer Queen')
                        return res

    p = 0

    # second move - q

    for pmc in pm:    #for each candidate pawn move
        gen = 0
        lineage[p,0] = gen   #generation
        lineage[p,1] = p    #id
        lineage[p,2] = -1   #parent
        lineage[p] = CalcMetrics(pmc, lineage[p])
        squares = GetSquares(pmc)
        for s in range(0,5):
            lineage[p,s+6] = squares[s]

        lineage[p,11] = 0   # 1 is stopper, 2 is winner

        if lineage[p,3] == 0:
            lineage[p,11] = 1

        qm = QueenMoves(pmc)
        ###################################
        # if no queen responses possible, move is a winner
        ###################################
        if qm.shape[0] == 0:
            lineage[p,11] = 2
            GotMove = True
            SolutionLevel = 1
            res.append(True)
            res.append(MakeBoard(lineage[p]))
            res.append(lineage)
            res.append('Winner')
            if verbose:
                print('Got a winner')
            return res

        p += 1

    # print(f'After 1 move, lineage has {lineage.shape[0]} elements ')

    if not GotMove:

        lineage = QueenPawn(lineage)

        maxgen = max(lineage[:,0])

        ###############################################
        # Check for win in 2 moves
        ###############################################
        
        if maxgen == 2:
            routes = []
            LastRound = lineage[lineage[:,0] == maxgen]
            routes = []
            
            for l in LastRound:
                lp = CalcPath(lineage,l[1])
                lp.append(l[11])
                routes.append(lp) 
                # print(lp)

            df_lp = pd.DataFrame(routes, columns = ['p1','q1','p2','Winner'])

            df_lp_g = df_lp.groupby(['p1', 'q1'], as_index=False)
            df_lp_g_a = df_lp_g.agg({'Winner':['count', 'sum']})
            df_lp_g_a.columns = ['p1', 'q1', 'count', 'sum']

            ps = df_lp_g_a.p1.unique()

            for thisp in ps:
                # print(f'evaluating {thisp}')
                df_lp_g_a_p = df_lp_g_a[df_lp_g_a['p1'] == thisp]
                df_lp_g_a_p2 = df_lp_g_a[(df_lp_g_a['p1'] == thisp) & (df_lp_g_a['sum'] == 2)]
                # print(df_lp_g_a_p.shape[0], df_lp_g_a_p2.shape[0])
                if df_lp_g_a_p.shape[0] == df_lp_g_a_p2.shape[0]:
                    res.append(True)
                    res.append(MakeBoard(lineage[thisp]))
                    res.append(lineage)
                    res.append('Winner in 2')
                    if verbose:
                        print('Got a winner')
                    return res

        ##################################################

        # no solution yet so return

    res.append(False)
    res.append(cmboard)
    res.append(lineage)
    res.append('No solution (yet)')

    return res

def Analysis1_A(cmboard, lineage):
    bests = BestMove(cmboard)
    bestId = bests[0]
    bestPct = bests[1]
    tot_moves = bests[2]
    thisboard = bests[3]

    res = []

    # print('Here',bestId, bestPct, tot_moves)

    if bestId >= 0 and bestPct > .6 and tot_moves > 5:
    # if bestId > 0 and bestPct > .6 and tot_moves > 5:
        res.append(True)
        res.append(thisboard)
        res.append(lineage)
        res.append(f'Pct is {bestPct}, total moves {tot_moves}')
    else:
        res.append(False)
        res.append(cmboard)
        res.append(lineage)
        res.append(f'No saved solution: Pct is {bestPct}, total moves {tot_moves}')

    return res

def BestMove(bboard):

    res = Analysis1(bboard)
    lineage = res[2]
    gen0 = lineage[lineage[:,0] == 0]
    pos = gen0[:,6:10]

    mc = 0
    bestPct = 0.00
    bestId = -1
    bestTot = 0

    for l in gen0:
        possMoves = l[6:11]
        sq = l[6:11]

        sqint = [int(i) for i in sq]
        b = bytes(sqint)
        bint = int.from_bytes(b,'big')
        # print(sq, bint)

        pgPawn_Occ = pgPawn[pgPawn['position'] == int(bint)]
        pgQueen_Occ = pgQueen[pgQueen['position'] == int(bint)]

        numpos_p_win = pgPawn_Occ.shape[0]
        numpos_q_win = pgQueen_Occ.shape[0]

        tot_moves = numpos_p_win + numpos_q_win 

        if tot_moves > 0:
            pct = numpos_p_win / (tot_moves)
        else:
            pct = 0.00

        if verbose:
            print(f'Move {mc} Pct {pct}, tot moves {tot_moves}')

        # nb = eng.MakeBoard(l)
        # bs.ShowBoard(nb)

        if pct > bestPct:
            bestPct = pct
            bestId = mc
            bestTot = tot_moves

        mc += 1

    if bestId >= 0:
        bo = MakeBoard(gen0[bestId])
    else:
        bo = bboard.copy()

    return [bestId, bestPct, bestTot, bo]

    # Analysis 2

def Analysis2(cmboard, lineage):

    GotMove = False

    maxgen = max(lineage[:,0])
    routes = []
    res = []
    GoodMoves = []
    # tb = len(lineage)

    if maxgen == 1:
        # no pawn responses to any queen move
        # therefore pawn loses
        # return cmboard
        res.append(True)
        res.append(cmboard.copy())
        res.append(lineage)
        res.append('Loser')
        return res

    if maxgen == 2:

        LastRound = lineage[lineage[:,0] == maxgen]

        for l in LastRound:
            route = CalcPath(lineage, l[1])
            # routes.append([route[0], route[1], route[2], route[3], route[4], lineage[l,3], lineage[l,4], lineage[l,5]])
            routes.append([route[0], route[1], route[2], l[3], l[4], l[5]])

        df_1 = pd.DataFrame(routes, columns = ['p1','q1','p2','CanEscape', 'RowsGained', 'Moves'])

        group = df_1.groupby(['p1', 'q1'], as_index=False)
        res_1 = group.agg({'CanEscape':['count', 'sum']})
        res_1.columns = ['p1', 'q1', 'pm_count', 'pm_esc_sum']

        res_1['blockedt'] = res_1['pm_count'] - res_1['pm_esc_sum']
        res_1['blocked'] = 0
        res_1.loc[res_1['blockedt'] >= 1, 'blocked'] = int(1)

        res_2 = res_1.groupby(['p1'], as_index=False).agg({'blocked': ['sum', 'count']})
        res_2.columns = ['pawn', 'moves_blocked', 'moves_count']

        res_3 = res_2[res_2['moves_blocked'] == res_2['moves_count']]
        ppp = res_3['pawn']

        # saveit = False
        # if saveit:
        #     df_1.to_csv(path+'df1.csv')
        #     res_1.to_csv(path+'res_1.csv')
        #     res_2.to_csv(path+'res_2.csv')
        #     res_3.to_csv(path+'res_3.csv')


    #############################################################
    # ppp has pawn moves that block all queen responses
    ############################################################
        lenp = len(ppp)

        if lenp > 0:
            for s in range(0,lenp):
                GoodMoves.append(ppp.iloc[s])

            GotMove = True
            GotSolution = 'Analysis 2'
            # print(f'got {lenp} solutions')

    if GotMove:
        # print('solution')
        SolutionLevel = 2
        sel = randrange(len(GoodMoves))
        p = GoodMoves[sel]
        res.append(True)
        res.append(MakeBoard(lineage[p]))
        res.append(lineage)
        res.append('Blocker after 2 moves')
        return res

    else:
        res.append(False)
        res.append(cmboard)
        res.append(lineage)
        res.append('No move from Analysis 2')
        return res
        
    # saveit = True
    saveit = False
    if saveit:
        df_1.to_csv(path+'df_3m.csv')
        # df_3m.to_csv(path+'df_3m.csv')

def Analysis3(cmboard, lineage):

    # print('Analysis3')

    GotMove = False
    GoodMoves = []
    res = []

    if not GotMove:

        lineage = QueenPawn(lineage)

        maxgen = max(lineage[:,0])
        
        if maxgen == 4:

            routes = []
            LastRound = lineage[lineage[:,0] == maxgen]
            
            for l in LastRound:
                route = CalcPath(lineage, l[1])
                routes.append([route[0], route[1], route[2], route[3], route[4], l[3], l[4], l[5]])

            # ########################################
            # # ChatGPT version

            # df_2 = pd.DataFrame(routes, columns = ['p1','q1','p2','q2','p3','CanEscape', 'RowsGained', 'Moves'])
            # res_2_1 = (
            #     df_2.groupby(['p1', 'q1','p2','q2'], as_index=False)
            #     .agg({'CanEscape':['count', 'sum']})
            #     .rename(columns={'count': 'pm_count', 'sum': 'pm_esc_sum'})
            #     .assign(
            #         blockedt=lambda x: x['pm_count'] - x['pm_esc_sum'],
            #         blocked=lambda x: (x['blockedt'] >= 1).astype(int)
            #     )
            # )

            # # ChatGPT version
            # ########################################

            ##############################
            # old version

            df_2 = pd.DataFrame(routes, columns = ['p1','q1','p2','q2','p3','CanEscape', 'RowsGained', 'Moves'])

            group_2 = df_2.groupby(['p1', 'q1','p2','q2'], as_index=False)
            res_2_1 = group_2.agg({'CanEscape':['count', 'sum']})
            res_2_1.columns = ['p1', 'q1', 'p2', 'q2', 'pm_count', 'pm_esc_sum']

            res_2_1['blockedt'] = res_2_1['pm_count'] - res_2_1['pm_esc_sum']
            res_2_1['blocked'] = 0
            res_2_1.loc[res_2_1['blockedt'] >= 1, 'blocked'] = int(1)

            thispath = pathlib.Path.cwd() / 'res_2_1.csv'
            
            if not thispath.exists():
                res_2_1.to_csv(thispath)

            # old version
            ###################################

            # print(list(res_2_1.columns))

            # print(res_2_1.head())

            ######################
        # GotMove = False

    ###########################################
            if not GotMove:

                thisqp = []
                ppass = []
                pfail = []

                ps = res_2_1.p1.unique()    #initial pawn moves

                for thisp in ps:    # for each first pawn move

                    thispgood = True

                    df_5m_sum_p = res_2_1[res_2_1['p1'] == thisp]
                    qs = df_5m_sum_p.q1.unique()    #get queen responses

                    qs_count = len(qs)
                    
                    qs_good_count = 0

                    for q in qs:    # for each queen response
                        
                        this_q_good = True
                        thisq = df_5m_sum_p[df_5m_sum_p['q1'] == q]
                        p2s = thisq.p2.unique() # get each pawn response (p2) in tree
                        
                        for p2 in p2s:  # for each p2
                            this_p2_good = False
                            thisqp.append([q,p2])
                            thisp2 = thisq[thisq['p2'] == p2]
                        
                            thisp2_sum = thisp2.groupby(['p1','q1','p2'], as_index=False).agg({'blocked': ['sum', 'count']})
                        
                            thisp2_sum.columns = ['p1', 'q1', 'p2', 'sum', 'count']

                            pw_pass = thisp2_sum[thisp2_sum['sum'] == thisp2_sum['count']]

                            if pw_pass.shape[0] == 0:
                                this_p2_good = False
                            else:
                                this_p2_good = True
                                break

                        if this_p2_good:
                            qs_good_count += 1

                    if qs_count == qs_good_count:
                        if thisp not in ppass:
                            ppass.append(thisp)
                    else:
                        if thisp not in pfail:
                            pfail.append(thisp)

                if len(ppass) > 0:
                    GotMove = True
                    
                    for s in range(0,len(ppass)):
                        # print(f'appending {ppass[s]} to GoodMoves')
                        GoodMoves.append(ppass[s])

        ######################
    if GotMove:
        # print('solution from df5')
        GotSolution = f'Analysis 3 from {len(GoodMoves)} choices'
        sel = randrange(len(GoodMoves))
        p = GoodMoves[sel]
        res.append(True)
        res.append(MakeBoard(lineage[p]))
        res.append(lineage)
        res.append(GotSolution)
        return res
    else:
        res.append(False)
        res.append(cmboard)
        res.append(lineage)
        res.append('No move from Analysis 3')
        return res

def Analysis4(cmboard, lineage):

    #################################################
    # no perfect solution
    # each pawn move given a score
    # .41 for hat
    # .41 for umbrella
    # .51 for umbrella to weak-side hat
    # 1.01 for Z, Z2 formations
    # extra moves * .10
    # blocker .41
    # removing
    #   prob of win based on saved games
    # removed


    FirstGen = lineage[lineage[:,0] == 0]
    moveScore = []
    cml = CalcLineage(cmboard)

    ##################################
    # hat
    ##################################

    possPawnMoves = FirstGen.shape[0]
    for m in range(0,possPawnMoves):
        moveScore.append([m, 0.00])

    # print(moveScore)

    if possPawnMoves == 1:
        sel = 0
    else:
        #########################
        newsel = -1
        tsel = 0
        for l in FirstGen:
            possMoves = l[6:11]
            qrow = GetPositions(cmboard)[0,4]
            if (qrow % 2) == 0: #even row
                gap1 = -3
                gap2 = -4
            else:
                gap1 = -4
                gap2 = -5
            # 0 compared with 1 and 2
            if possMoves[0] - possMoves[1] == gap1 and possMoves[0] - possMoves[2] == gap2 and possMoves[0] - possMoves[4] == -8:
                moveScore[tsel][1] += .41
            # 0 compared with 2 and 3
            if possMoves[0] - possMoves[2] == gap1 and possMoves[0] - possMoves[3] == gap2 and possMoves[0] - possMoves[4] == -8:
                moveScore[tsel][1] += .41
            # 0 compared with 2 and 3
            if possMoves[1] - possMoves[2] == gap1 and possMoves[1] - possMoves[3] == gap2 and possMoves[1] - possMoves[4] == -8:
                moveScore[tsel][1] += .41

            tsel += 1

    # print(moveScore)
    ########################################
    # umbrella
    #######################################

    umb1 = [1,2,2]
    umb2 = [1,3,2]
    qdiffs = [-1, 3, 4, 7]
    tsel = 0

    for l in FirstGen:
        sq = l[6:11]
        pdiffs = [sq[1]-sq[0],sq[2]-sq[1],sq[3]-sq[2]]   #,sq[4]-sq[3]]
        qdiff = sq[4]-sq[3]
        if (pdiffs == umb1 or pdiffs == umb2) and (qdiff in qdiffs):
            # print(f'possible umbrella {sq}, {pdiffs}, {qdiff}')
            moveScore[tsel][1] += .41
        # print(sq, pdiffs)

        tsel += 1

    # print(moveScore)
    ############################################
    # umbrella to weak-side hat
    ############################################

    umbrella = False
    sq = cml[6:11]
    pdiffs = [sq[1]-sq[0],sq[2]-sq[1],sq[3]-sq[2]]   #,sq[4]-sq[3]]
    qdiff = sq[4]-sq[3]
    if (pdiffs == umb1 or pdiffs == umb2) and (qdiff in qdiffs):
        umbrella = True
    if umbrella:
        if verbose:
            print(f'Umbrella {umbrella}')
        pos = GetPositions(cmboard)
        cols = pos[1,:]
        mincol = min(cols)
        # if mincol == 2:
        #     print('weak-side left')
        #     # hat with move to the left
        # else:
        #     print('weak-side right')
        #     # hat with move to the right

        GotMove = False
        tsel = 0
        for l in FirstGen:
            h = IsHat(l)
            # print(f'{tsel} is hat {h}')
            if h:
                # print(f'is hat {h}')
                # bs.ShowBoard(n)
                # print()
                # print(pml)
                chg = l[6] - cml[6]     #cml = CalcLineage(cmboard)
                if chg == 0 and mincol == 2:    # mincol == 2 means left side weak
                    # print('hat left')
                    GotMove = True
                    moveScore[tsel][1] += .51
                    break
                if chg != 0 and mincol == 1:
                    # print('hat right')
                    GotMove = True
                    moveScore[tsel][1] += .51
                    break
            tsel += 1

    # print(moveScore)
    ############################################
    # Z
    ############################################
    mincol = min(GetPositions(cmboard)[1,:])
    pos = cml[6:11]
    # print(pos)
    diffs = [pos[1] - pos[0], pos[2] - pos[1], pos[3] - pos[2], pos[4] - pos[3]]
    # print(diffs)
    if diffs == [1, 8, 1, 3] and mincol == 1:
        tsel = 0
        for l in FirstGen:
            pos = l[6:11]
            diffs = [pos[1] - pos[0], pos[2] - pos[1], pos[3] - pos[2], pos[4] - pos[3]]
            if diffs == [3, 5, 1, 3]:
                moveScore[tsel][1] += 1.01
            tsel += 1

    
    # print(moveScore)
    ############################################
    # Z2
    ############################################
    mincol = min(GetPositions(cmboard)[1,:])
    pos = cml[6:11]
    # print(pos)
    diffs = [pos[1] - pos[0], pos[2] - pos[1], pos[3] - pos[2], pos[4] - pos[3]]
    # print(diffs)
    if diffs == [3, 5, 1, 7] and mincol == 0:
        tsel = 0
        for l in FirstGen:
            pos = l[6:11]
            diffs = [pos[1] - pos[0], pos[2] - pos[1], pos[3] - pos[2], pos[4] - pos[3]]
            if diffs == [2, 3, 1, 7]:
                moveScore[tsel][1] += 1.01
            tsel += 1
    

    # print(moveScore)
    ############################################
    # extra Moves
    ############################################
    
    tsel = 0

    for l in FirstGen:

        sq = l[6:11]
        sqint = [int(i) for i in sq]
        b = bytes(sqint)
        bint = int.from_bytes(b,'big')
        
        exMoves = l[5] - l[4]
        if verbose:
            print(f'{l}, exM {exMoves}, {bint}')

        moveScore[tsel][1] += exMoves * .1
        tsel += 1

    ############################################
    # killer queen
    ############################################

    kq = isKillerQueen(cmboard)
    if kq[0]:
        print(f'is killer')
        bs.ShowBoard(kq[1])
        pos = GetPositions(kq[1])
        # pos = eng.GetPositions(kq[1])
        qpos = [pos[0,4],pos[1,4]] 
        print(f'must block {qpos}')

        # pmkq = PawnMoves(cmboard)
        # for p in pmkq:
        tsel = 0

        for l in FirstGen:
            bo = MakeBoard(l)
            ppos = GetPawnPositionsList(bo)
            for pp in ppos:
                # print(f'can {pp} block {qpos}?')
                if pp == qpos:
                    # print('got blocker')
                    # bs.ShowBoard(p)

                    moveScore[tsel][1] += 1.01

                    # res.append(True)
                    # res.append(p)
                    # res.append(lineage)
                    # res.append('Killer Queen blocker')
                    if verbose:
                        print('Blocking Killer Queen')
                    return res
            tsel += 1

    # print(moveScore)
    ############################################
    # blockers
    #############################################

    # res = Analysis1(cmboard)
    # lineage = res[2]

    # Gen0 = lineage[lineage[:,0] == 0]
    Gen1 = lineage[lineage[:,0] == 1]
    Gen2 = lineage[lineage[:,0] == 2]
    # print(Gen0)

    # Gen1 critical path list
    # Gen2[6:11] in Gen1 critical path
    # need min one pawn blocker for each queen

    GoodPawnMoves = []
    Exmoves = []

    for p in FirstGen:  #each pawn
        p_id = p[1]
        pq = Gen1[Gen1[:,2] == p_id]
        pq_count = len(pq)  # number of queen children
        # print(f'pawn {p_id} has {pq_count} children')
        p_ch_blocked = 0
        pq_count_b = 0
        qpass = []
        for pq_i in pq:  # check queens
            bo = MakeBoard(pq_i)
            cpl = CriticalPathListSquares(bo)
            # print(f'{p_id} cpl is {cpl}')
            # cpl.reverse()
            q_id = pq_i[1]
            # print(f'\tqueen {q_id}, child of pawn {p_id} has critial path {cpl}')
            pqp = Gen2[Gen2[:,2] == q_id]
            pqp_count = len(pqp)  # number of queen children
            # print(f'\tqueen {q_id} has {pqp_count} children')
            
            for pqp_i in pqp:   # each pawn move for queen
                pqp_id = pqp_i[1]
                pqp_pos = pqp_i[6:11]
                blocked = False
                lst3 = [value for value in list(pqp_pos) if value in cpl]
                if len(lst3) > 0:
                    # if pq_count_b == 0:
                    pq_count_b += 1
                    blocked = True
                    if q_id not in qpass:
                        qpass.append(q_id)
                    Exmoves.append([pqp_id, pqp_i[5]- pqp_i[4]])
                    # print(f'\t\tpawn {pqp_id}, child of queen {q_id} has positions {list(pqp_pos)}, can block {blocked}')
                    # print(f'{pq_count} queeens, {pq_count_b} blocked')
                    # break
                else:
                    blocked = False

                
                # print(f'{pq_count_b} queen moves blocked')
            # print()

            if pq_count == len(qpass):
            # if pq_count == pq_count_b:
                if verbose:
                    print(f'pawn {p_id} can block all queen moves')
                bo = MakeBoard(lineage[p_id])
                if verbose:
                    bs.ShowBoard(bo)
                GoodPawnMoves.append(p_id)

    msa = np.array(Exmoves)
    if verbose:
        print(msa.shape)
    # msamax = max(msa[:,1])
    # print(max(msa[:,1]))
    if msa.shape[0] > 0:
        tm = msa[msa[:,1] == max(msa[:,1])]
        # print(tm)

        index = randrange(len(tm))
        ps = tm[index,0]
        psp = CalcPath(lineage, ps)
        # print(psp[0])
        tsel = psp[0]
        moveScore[tsel][1] += .41

    ############################################
    # x-range
    #############################################
    # sq = list(cml[6:10])
    # ss = [GetRowCol(s)[0] for s in sq]
    # minx, maxx = min(ss), max(ss)
    # cxdiff = maxx - minx
    # print(f'cxdiff is {cxdiff}')

    # tsel = 0

    # for p in FirstGen:
    #     sq = list(p[6:10])
    #     # sq = [5, 10, 14, 19]
    #     ss = [GetRowCol(s)[0] for s in sq]
    #     minx, maxx = min(ss), max(ss)
    #     xdiff = maxx - minx
    #     if xdiff >= 2:
    #         # =F5*0.1 + (F5-F4)*0.2
    #         moveScore[tsel][1] -= (xdiff * 0.1) + (xdiff - cxdiff) * 0.2
    #     tsel += 1


    # replacing first blockers

    # cpl = CriticalPathList(cmboard)
    # print(f'Critial path is {cpl}')

    # if len(cpl) <= 7:   # change - only block if critical path is short
    #     # print(f'Critial path is {cpl}')
    #     bl = PawnOneMoveList(cmboard)
    #     bl_sqs = []

    #     for b in bl:
    #         if b in cpl:
    #             bl_sq = Square(b[0], b[1])  # pawn move in blocker list
    #             bl_sqs.append(bl_sq)

    #             print(b, bl_sq)
    #             # sq = l[6:11]

    #     print(f'{len(bl_sqs)} blockers, {bl_sqs}')

    #     tsel = 0

    #     if len(bl_sqs) > 0: #have a blocker
    #         bl = bl_sqs[randrange(0, len(bl_sqs))]
    #         print('have a blocker')

    #         for l in FirstGen:
    #             sq = l[6:11]

    #             # if bl in sq:
    #             for b in bl_sqs:
    #                 if b in sq:
    #                     cex = cml[5]-cml[4] #cml: starting board lineage
    #                     nex = l[5]-l[4]
    #                     print(f'Current exMoves is {cex}, this move is {nex}')
    #                     if nex >= cex:
    #                         moveScore[tsel][1] += .41

    #             tsel += 1

    # replacing first blockers

    ############################################
    # removing
    # prob of win
    ############################################

    # pg = pd.read_csv(path+'game.csv')

    # pgpw = pg[pg['winner']=='Pawns']
    # pgqw = pg[pg['winner']=='Queen']

    # dfg = pd.read_csv(path+'game_moves.csv')

    # pgm = pd.merge(pgpw, dfg, on="game_id")
    # pgmq = pd.merge(pgqw, dfg, on="game_id")

    # tsel = 0
    # for l in FirstGen:
    #     # sq = GetSquares(tboard)
    #     sq = l[6:11]
    #     sqint = [int(i) for i in sq]
    #     b = bytes(sqint)
    #     bint = int.from_bytes(b,'big')

    #     print(sq, bint)

    #     pgmp = pgm[(pgm['game_id'] > 0)]
    #     pgmpw = pgmp[pgmp['position'] == bint]

    #     # queen wins
    #     pgmpq = pgmq[(pgmq['game_id'] > 0)]
    #     pgmpwq = pgmpq[pgmpq['position'] == bint]

    #     numpos_p_win = pgmpw.shape[0]
    #     numpos_q_win = pgmpwq.shape[0]
    #     totpos = numpos_p_win + numpos_q_win

    #     if totpos > 0:
    #         pct = numpos_p_win / totpos
    #     else:
    #         pct = 0.00

    #     moveScore[tsel] += pct

    #     tsel += 1

    # removed

    #########################################
    # evaluate result
    ##########################################

    # max_value = max(moveScore)
    max_value = max([el[1] for el in moveScore])
    # print(f'max is {max_value}')
    filtered = filter(lambda score: score[1] == max_value, moveScore)
    # index = moveScore.index(max_value)
    lf = list(filtered)
    # print(len(lf),lf)

    index = randrange(len(lf))
    sel = lf[index][0]
    # print(lf[sel])
    
    res = []
    res.append(True)
    res.append(MakeBoard(lineage[sel]))
    res.append(lineage)
    res.append(f'from {moveScore} {sel} is the best move')
    return res

def CanBlockQueen(queenmove):
    qcpl = CriticalPathList(queenmove)
    # print(f'queen move critical path {qcpl}')
    pm = PawnMoves(queenmove)
    CanBlock = False
    for p in pm:
        ppos = GetPawnPositionsList(p)
        apos = np.array(ppos)
        if max(apos[:,0]) <= 2:
            CanBlock = True
            break
        for pp in ppos:
            if pp in qcpl:
                CanBlock = True

    return CanBlock

def KillerQueen(board):
    qm = QueenMoves(board)
    for q in qm:
        if not CanBlockQueen(q):
            # print('Killer Queen')
            # bs.ShowBoard(q)
            return [True,q]
    return [False,board]

def RandomQueenMove(qmboard):
    qm = QueenMoves(qmboard)
    if qm.shape[0] == 0:
        retboard = qmboard.copy()
    else:
        sm = randrange(0, qm.shape[0])
        retboard = qm[sm]
    return retboard

def CalcQueenMove(qmboard): #here

    # kq = KillerQueen(qmboard)
    # if kq[0]:
    #     # print(f'Killer queen')
    #     return kq[1]

    RandValue = 5
    sel = randrange(RandValue)
    RandomMove = False
    if sel == RandValue - 1:
        RandomMove = True

    # RandomMove = False

    qm = QueenMoves(qmboard)
    retboard = qmboard.copy()
    if qm.shape[0] == 0:
        return retboard

    bestPct = -1.0
    bestTot = -1

    for q in qm:
        squares = GetSquares(q)
        # print(squares)
        sq = squares[0:5]
        sqint = [int(i) for i in sq]
        b = bytes(sqint)
        bint = int.from_bytes(b,'big')
        

        pgPawn_Occ = pgPawn[pgPawn['position'] == int(bint)]
        pgQueen_Occ = pgQueen[pgQueen['position'] == int(bint)]

        numpos_p_win = pgPawn_Occ.shape[0]
        numpos_q_win = pgQueen_Occ.shape[0]

        tot_moves = numpos_p_win + numpos_q_win 

        if tot_moves > 0:
            pct = numpos_q_win / (tot_moves)
        else:
            pct = 0.00
        if verbose:
            print(bint, pct)
            bs.ShowBoard(q)

        if pct > bestPct and tot_moves > 0:
            bestPct = pct
            bestId = q
            bestTot = tot_moves

    # print(f'Winning % for queen is {bestPct} based on {bestTot} occurrences')
    # if bestPct > -1:
    #     bs.ShowBoard(bestId)

    if RandomMove:
        # print('Random move')
        sm = randrange(0, qm.shape[0])
        retboard = qm[sm]

    else:
        if bestPct >= .25 and bestTot >= 5:
            if verbose:
                print(f'selection based on {bestPct} on {bestTot} occurrences')
                bs.ShowBoard(bestId)
            retboard = bestId
            return retboard

        qme = CanEscape(qmboard)
        # print(f'can escape {qme}')

        cp = CriticalPath(qmboard)
        cmm = np.max(cp)

    # print(qm.shape)

        if qme:
            cpm = 50
            bd = 0
            spm = -1
            sp = 1000
            # for q in qm:
            for bd in range(0,qm.shape[0]):
                # print()
                cp = CriticalPath(qm[bd])
                cpm = np.max(cp)
                if cpm < sp:
                    sp = cpm
                    spm = bd

            # print(f'move {spm} has shortest path {sp}')
            # bs.ShowBoard(qm[spm])
            retboard = qm[spm]

        else:
            # print(f'cant escape so random move')
            if RandomMove:    # completely random move
                sm = randrange(0, qm.shape[0])
                # print(f'random move {sm}')
                # bs.ShowBoard(qm[sm])
                retboard = qm[sm]
            else:
                # print('try to go forward')
                qpos = np.where(qmboard == 5)
                qrow = qpos[0][0]
                qcol = qpos[1][0]
                # print(f'current row is {qrow}')
                posm = []
                for bd in range(0,qm.shape[0]):
                    tpos = np.where(qm[bd] == 5)
                    trow = tpos[0][0]
                    if trow < qrow:
                        # print(f'{bd} is a forward move')
                        posm.append(bd)

                if len(posm) > 0:
                    # print(f'{len(posm)} possible forward moves')
                    sm = randrange(0, len(posm))
                    # print(f'random move {sm}')
                    # bs.ShowBoard(qm[sm])
                    retboard = qm[sm]
                else:
                    sm = randrange(0, qm.shape[0])
                    # print(f'cant go forward to random move {sm}')
                    # bs.ShowBoard(qm[sm])
                    retboard = qm[sm]

    return retboard

def QForce(blb):

    nlb = blb.copy()
    pos = GetPositions(blb)
    pieces = pos.shape[1] - 1
    qx = pos[0][pieces]
    qy = pos[1][pieces]
    px = pos[0][0:pieces]
    minpx = min(px)

    m = 0

    r1 = [] #starting positions
    r1.append([qx,qy])
    r2 = [] #completed

    while len(r1) > m:
        r = r1[m]
        if r not in r2:
            r2.append(r)
            qx, qy = r[0], r[1]
            # qval = startval if nlb[qx,qy] == 5 else nlb[qx,qy] + 5
            qval = 5 * (7 - qx)
            for dx in range(-1,2,2):
                for dy in range(-1,2,2):
                    nx = qx + dx
                    ny = qy + dy

                    if 0 <= nx < 8 and 0 <= ny <= 7: 
                        # if blb[nx, ny] == 0:
                        if nlb[nx, ny] == 0:
                            newpos = [nx, ny]

                            if newpos not in r1:    # and nx > 0:
                                nlb[nx, ny] = qval

                                if nx > 0:
                                # if 1 == 1:
                                    r1.append(newpos)
        m += 1

    qres = np.sum(nlb)

    return qres



# # # import time
# # # start_time_Guru99 = time.time()

# cmboard = LoadStart()
# cmboard = MakeBoardFromPosition(60500155422)
# # # cpl = CriticalPathListSquares(cmboard)
# # # print(cpl)


# # # # # # # # cml = CalcLineage(cmboard)

# bs.ShowBoard(cmboard)


# # # # # # print()

# nboard = CalcMove(cmboard)

# bs.ShowBoard(nboard)



# # # end_time_Guru99 = time.time()
# # # print("Time elapsed: ", end_time_Guru99 - start_time_Guru99)


