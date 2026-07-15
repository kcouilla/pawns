# import pygame
import numpy as np
import os
import csv
path='C:\\Users\\kcoui\\source\\repos\\Python\\pawns\\files\\'

# intColour1 = 'burlywood'
# intColour2 = 'Black'
# green = (0, 255, 0)
# blue = (0, 0, 128)

squares = 8
rectsize = 99
squaresize = 100
size = (800, 800)

def initboard(LoadStart = True):
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

        # print(board)

    else:
    
        p = 1
        for col in range(0,squares,2):
            # board[0,col] = p
            board[0,col] = 1
            p+= 1

        row, col = 7,3
        board[row,col] = 5

        # print(board)

    return board

def GetPositions(board):

    pos = np.empty([2,5], dtype=int)
    
    rs = np.where(board == 1)
    for p in range(0,4):
        pos[0,p] = int(rs[0][p])
        pos[1,p] = int(rs[1][p])

    qpos = np.where(board == 5)
    pos[0,4] = int(qpos[0][0])
    pos[1,4] = int(qpos[1][0])

    return(pos)

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
    # m4 = NextMove(board,m3, InclPath)
    # m5 = NextMove(board,m4, InclPath)
    # m6 = NextMove(board,m5, InclPath)
    # m7 = NextMove(board,m6, InclPath)

    mboard = board.copy()

    for m in m1:
        mboard[m[0],m[1]] = 6

    for m in m2:
        mboard[m[0],m[1]] = 7

    for m in m3:
        mboard[m[0],m[1]] = 8

    # for m in m4:
    #     mboard[m[0],m[1]] = 9

    # for m in m5:
    #     mboard[m[0],m[1]] = 10

    # for m in m6:
    #     mboard[m[0],m[1]] = 11

    # for m in m7:
    #     mboard[m[0],m[1]] = 12

    return mboard

def SetOfPossibleMoves(board):
    qpos = np.where(board == 5)
    qposx = int(qpos[0][0])
    qposy = int(qpos[1][0])

    m = []
    ms = []
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

    if len(m1) > 0:
        ms.append(m1)
    
    if len(m2) > 0:
        ms.append(m2)

    if len(m3) > 0:
        ms.append(m3)

    if len(m4) > 0:
        ms.append(m4)

    if len(m5) > 0:
        ms.append(m5)

    if len(m6) > 0:
        ms.append(m6)

    if len(m7) > 0:
        ms.append(m7)
    # ms.append(m2)
    # ms.append(m3)
    # ms.append(m4)
    # ms.append(m5)
    # ms.append(m6)
    # ms.append(m7)

    # m1.append(NextMove(board,m1, InclPath))
    # m1.append(NextMove(board,m1, InclPath))
    # m1.append(NextMove(board,m1, InclPath))
    # m1.append(NextMove(board,m1, InclPath))
    # m1.append(NextMove(board,m1, InclPath))
    # m1.append(NextMove(board,m1, InclPath))

    # mboard = board.copy()

    # for m in m1:
    #     mboard[m[0],m[1]] = 6

    # for m in m2:
    #     mboard[m[0],m[1]] = 7

    # for m in m3:
    #     mboard[m[0],m[1]] = 8

    # for m in m4:
    #     mboard[m[0],m[1]] = 9

    # for m in m5:
    #     mboard[m[0],m[1]] = 10

    # for m in m6:
    #     mboard[m[0],m[1]] = 11

    # for m in m7:
    #     mboard[m[0],m[1]] = 12

    return ms

def NextMove(board, m1, includeCurrent = True):

    m2 = []

    for m in m1:
    # print(m)
        m1x = m[0]
        m1y = m[1]
        # print(m1x, m1y)
        for x in range(-1,2,2): # changed from 1 to 2
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

# import basic_stuff as bs
# import numpy as np
# import importlib
# importlib.reload(bs)

def GapExists(board):
    pos = GetPositions(board)

    px = pos[0][0:4]
    py = pos[1][0:4]

    qx = int(pos[0][4])
    qy = int(pos[1][4])

    minx = int(min(px))
    newboard = CalcPossibleMoves(board)
    steps = np.where(newboard > 5)
    thru = np.where(steps[0] <= minx)

    if len(thru[0]) == 0 or int(qx - minx) > 2:
        return False
    else:
        return True

def MakeBoard(board,p,m):
    # print(board[p[0], p[1]])
    board[p[0], p[1]] = 0
    board[m[0], m[1]] = 1
    return board

def ShowBoard(xboard):
    sboard = xboard.copy()
    for x in range(0,8):
        for y in range(0,8):
            if sboard[x,y] == 1:
                sboard[x,y] = 111
            if sboard[x,y] == 5:
                sboard[x,y] = 50
            if ((x+y) % 2) == 1:
                sboard[x,y] = 7

            # if sboard[x,y] > 5:
            #     sboard[x,y] = sboard[x,y] * 111
    # print('<div style=style="font-size: 24px">')
    
    print(sboard, '\n')

    # print('</div>')

def ShowBoard_Return(xboard):
    sboard = xboard.copy()
    for x in range(0,8):
        for y in range(0,8):
            if sboard[x,y] == 1:
                sboard[x,y] = 111
            if sboard[x,y] == 5:
                sboard[x,y] = 50
            if ((x+y) % 2) == 1:
                sboard[x,y] = 7
    # print(sboard)
    return sboard

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
                else:   #consider moves of all pieces from this starting point
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

    # print(pos)
def CanBlockGap(board): #need to consider possible queen moves
    xboard = board.copy()

    qboards = np.zeros((4, 8, 8), dtype=np.int8)
    pos = GetPositions(xboard)

    qx = int(pos[0][4])
    qy = int(pos[1][4])
        # print(pos)
    GotMove = True
    #need to be able to block all queen moves
    qm=[]
    qc = 0
    for l2x in range(-1,2,2):
        for l2y  in range(-1,2,2):
        # check if legal
            if 0 <= qx+l2x <= 7 and 0 <= qy+l2y <= 7:
                l2m = [qx+l2x,qy+l2y]
                qm.append(l2m)

    for q in range(0,len(qm)):  #4 possible queen moves
        b = xboard.copy()
        nqx = qm[q][0]  # new queen x
        nqy = qm[q][1]  # new queen y
        #move queen 
        if b[nqx][nqy] == 0:    # if cell not occupied
            b[qx,qy] = 0
            b[nqx][nqy] = 5
            qboards[qc] = b
            qc += 1

    testBoards = np.resize(qboards,(qc,8,8))

    Blocked = 0

    for qcn in range(0,qc): #for every queen move

        for p in range(0,4):    # for each pawn
            row = int(pos[0][p])    #get current row and col
            col = int(pos[1][p])

            if row + 1 <= 7 and col - 1 >= 0:
                if testBoards[qcn][row+1][col-1] == 0:
                    pboard = testBoards[qcn].copy()
                    pboard[row][col] = 0
                    pboard[row + 1][col - 1] = 1

                    if not GapExists(pboard):
                        Blocked += 1
                        break

            if row + 1 <= 7 and col + 1 <= 7: 
                if testBoards[qcn][row+1][col+1] == 0:
                    pboard = testBoards[qcn].copy()
                    pboard[row][col] = 0
                    pboard[row + 1][col + 1] = 1

                    if not GapExists(pboard):
                        Blocked += 1
                        break

    if qc == Blocked:
        return True
    else:
        return False

def x_CanBlockGap(board):
    pos = GetPositions(board)
    # print(pos)
    GotMove = False
    for p in range(0,4):
        row = int(pos[0][p])
        col = int(pos[1][p])
        if row + 1 <= 7 and col - 1 >= 0:
            if board[row+1][col-1] == 0:
                pboard = board.copy()
                pboard[row][col] = 0
                pboard[row + 1][col - 1] = 1
                if not GapExists(pboard):
                    GotMove = True
                    break
        if row + 1 <= 7 and col + 1 <= 7: 
            if board[row+1][col+1] == 0:
                pboard = board.copy()
                pboard[row][col] = 0
                pboard[row + 1][col + 1] = 1
                if not GapExists(pboard):
                    GotMove = True
                    break

    if GotMove:
        return True
    else:
        return False




