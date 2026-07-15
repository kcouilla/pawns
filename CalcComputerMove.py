import numpy as np
import pandas as pd
import basic_stuff as bs

def PawnMoves(board):

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

                    ##### removing this condition
                    # if not (bs.GapExists(b) and not bs.GapExists(board)):
                    #     boards[m] = b
                    #     m += 1
                    #################

                    if not bs.GapExists(b) or bs.CanBlockGap(b): 
                        boards[m] = b
                        m += 1

                    # boards[m] = b
                    # m += 1

    # t = boards.copy()
    
    # boards = np.zeros((m, 8, 8), dtype=np.int8)
    # for tt in range(0,m):
    #     boards[tt] = t[tt]

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

    # t = boards.copy()
    
    # boards = np.zeros((qc, 8, 8), dtype=np.int8)
    # for tt in range(0,qc):
    #     boards[tt] = t[tt]

    # return boards

def GetMaxYGap(board):
    pos = bs.GetPositions(board)
    px = pos[0][0:4]
    py = pos[1][0:4]

    py.sort()
    ygaps = []

    ygaps.append(py[0])
    ygaps.append(7 - py[3])

    cg = 0
    for ys in range(1,4):
        tlg = py[ys] - py[ys-1]
        if tlg > cg:
            cg = tlg

    ygaps.append(cg)

    return max(ygaps)

def path(pawn, Gaps):
    child = pawn
    top = False
    seq = [child]
    while not top:
        parent = Gaps[child,1]
        if parent == -1:
            top = True
        else:
            seq.append(parent)
            child = parent

    seq.reverse()
    # print(seq)

    return seq

def CalcMove(board):

    print('Before')
    bs.ShowBoard(board)

    StartCount, EndCount, SetStart = 0,0,0

    pboards = PawnMoves(board)
    pb = pboards.shape[0]

    lineage = np.zeros((pb,4), dtype=int)

    StartCount = EndCount   # number of pawn moves
    EndCount = StartCount + pb  # total number
    lineage = np.resize(lineage,(EndCount,4))

    for qq in range(StartCount,EndCount):
        lineage[qq,0] = qq
        lineage[qq,1] = -1  #parent, ie pawn move 
        lineage[qq,2] = 1
        lineage[qq,3] = 1

    # tb = np.concatenate((boards, pboards))
    boards = pboards.copy()
    # boards = tb.copy()

    SetStart = 0

    for iter in range(0,3,2):
        StartCount = SetStart
        SetStart = EndCount
        for n in range(StartCount,EndCount):    #0, number of pawn moves
            # print(f'board {n}')
            qboards = QueenMoves(boards[n])
            qb = qboards.shape[0]
            # print(f'{qb} boards returned')

            StartCount = EndCount   # number of pawn moves
            EndCount = StartCount + qb  # total number
            # lineage = np.resize(lineage,(EndCount,2))
            lineage = np.resize(lineage,(StartCount + qb,4))

            for qq in range(StartCount,EndCount):
                lineage[qq,0] = qq
                lineage[qq,1] = n  #parent, ie pawn move 
                lineage[qq,2] = 5
                lineage[qq,3] = 2 + iter

            tb = np.concatenate((boards, qboards))
            boards = tb.copy()

        StartCount = SetStart
        SetStart = EndCount
        
        for bbb in range(StartCount,EndCount):
            pboards = PawnMoves(boards[bbb])
            pb = pboards.shape[0]

            StartCount = EndCount   # number of pawn moves
            EndCount = StartCount + pb  # total number
            lineage = np.resize(lineage,(EndCount,4))

            for qq in range(StartCount,EndCount):
                lineage[qq,0] = qq
                lineage[qq,1] = bbb  #parent, ie pawn move 
                lineage[qq,2] = 1
                lineage[qq,3] = 3 + iter

            tb = np.concatenate((boards, pboards))
            boards = tb.copy()

    # print(boards.shape)
    # end = time.time()
    # print(f'Create boards elapsed time: {end - start} seconds')
    # start = time.time()
    nb = boards.shape[0]

    Gaps = np.zeros((nb, 6), dtype=int)
    for nbn in range(0,nb):
        # print(f'Gap exists for {nbn}: {bs.GapExists(boards[nbn])}')
        Gaps[nbn,0] = lineage[nbn,0]    # id
        Gaps[nbn,1] = lineage[nbn,1]    # parent
        Gaps[nbn,2] = lineage[nbn,2]    # type
        Gaps[nbn,3] = lineage[nbn,3]    #level
        Gaps[nbn,4] = bs.GapExists(boards[nbn]) #gap
        Gaps[nbn,5] = bs.CanBlockGap(boards[nbn]) #can block

    # end = time.time()
    # print(f'Create Gaps elapsed time: {end - start} seconds')
    # start = time.time()

    df_all = pd.DataFrame(Gaps)
    df_all = df_all.rename(columns={0: 'id', 1: 'parent', 2: 'type', 3: 'level', 4: 'gap', 5: 'canBlock'})

    df_p1 = df_all[df_all.level.isin([1])]
    df_q1 = df_all[df_all.level.isin([2])]

    GoodMoves = []
    GoodFirstMoves = []
    OkMoves = []
    OkFirstMoves = []
    NotGreatMoves = []
    NotGreatMoves = []
    InitialBlock = []

    for p1 in df_p1.itertuples(index=False):   #pawn move 1
        # print(f'{row} - pawn id = {row[0]}, parent = {row[1]}')
        pawn = p1[0]
        if p1[4] == 0: #inital gap exists and can be blocked
            InitialBlock.append(pawn)

        df_q1 = df_all[df_all.parent.isin([pawn])]
        BlockAll = True
        
        for q1 in df_q1.itertuples(index=False):
            queen = q1[0]
            canBlock = q1[5]
            if canBlock == 0:
                BlockAll = False
            # print(f'\tpawn id = {pawn}, queen id = {queen}, gap = {q1[4]}, canBlock = {q1[5]}')

            df_p2 = df_all[df_all.parent.isin([queen])]
            
            for p2 in df_p2.itertuples(index=False):   #pawn move 2
                pawn2 = p2[0]
                # print(f'\tpawn id = {pawn2}')
                df_q2 = df_all[df_all.parent.isin([pawn2])]
                BlockAll2 = True
                
                for q2 in df_q2.itertuples(index=False): #queen move 2
                    queen2 = q2[0]
                    canBlock2 = q2[5]
                    if canBlock2 == 0:
                        BlockAll2 = False
                    # print(f'\t\tpawn id = {pawn2}, queen id = {queen2}, gap = {q2[4]}, canBlock = {q2[5]}')
                    df_p3 = df_all[df_all.parent.isin([queen2])]
                    
                    for p3 in df_p3.itertuples(index=False):   #pawn move 2
                        pawn3 = p3[0]
                        # print(f'\t\t\tpawn id = {pawn3}')
                        df_q3 = df_all[df_all.parent.isin([pawn3])]
                        BlockAll3 = True
                        
                        for q3 in df_q3.itertuples(index=False): #queen move 2
                            queen3 = q3[0]
                            canBlock3 = q3[5]
                            if canBlock3 == 0:
                                BlockAll3 = False
                            # print(f'\t\t\t\tpawn id = {pawn3}, queen id = {queen3}, gap = {q3[4]}, canBlock = {q3[5]}')

                        if BlockAll and BlockAll2 and BlockAll3:
                            # print(f'{pawn3} looks good - path: {Gaps[443,1]}, {Gaps[Gaps[443,1],1]}')
                            # print(f'{pawn3} looks good - path: {path(pawn3, Gaps)}')
                            GoodMoves.append(pawn3)
                            pathtoMove = path(pawn3, Gaps)
                            GoodFirstMoves.append(pathtoMove[0])

                        if BlockAll and BlockAll2 and not BlockAll3:
                            # print(f'{pawn3} looks good - path: {Gaps[443,1]}, {Gaps[Gaps[443,1],1]}')
                            # print(f'{pawn3} looks good - path: {path(pawn3, Gaps)}')
                            OkMoves.append(pawn3)
                            pathtoMove = path(pawn3, Gaps)
                            OkFirstMoves.append(pathtoMove[0])

                        if BlockAll and not BlockAll2 and not BlockAll3:
                            # print(f'{pawn3} looks good - path: {Gaps[443,1]}, {Gaps[Gaps[443,1],1]}')
                            # print(f'{pawn3} looks good - path: {path(pawn3, Gaps)}')
                            NotGreatMoves.append(pawn3)
                            pathtoMove = path(pawn3, Gaps)
                            NotGreatMoves.append(pathtoMove[0])

        #                 print(f'\t\tpawn {pawn3} can block all queen moves = {BlockAll3}')
            
        #         print(f'\tpawn {pawn2} can block all queen moves = {BlockAll2}')

        # print(f'pawn {pawn} can block all queen moves = {BlockAll}')

    # end = time.time()
    # print(f'Analysis elapsed time: {end - start} seconds')
    # start = time.time()

    GoodSet = set(GoodFirstMoves)
    Good_move_list = list(GoodSet)
    num_Good_moves = len(Good_move_list)

    OkSet = set(OkMoves)
    OK_move_list = list(OkSet)
    num_OK_moves = len(OK_move_list)

    NotGreatSet = set(NotGreatMoves)
    NotGreat_move_list = list(NotGreatSet)
    num_NotGreat_moves = len(NotGreat_move_list)

    InitialBlockSet = set(InitialBlock)
    InitialBlocklist = list(InitialBlockSet)
    num_InitialBlock_moves = len(InitialBlocklist)

    # print('start')
    # bs.ShowBoard(board)

    move_list = []
    Using = ''

    if num_InitialBlock_moves > 0:
        move_list = InitialBlocklist
        Using = 'InitialBlocklist'

    if num_NotGreat_moves > 0:
        move_list = NotGreat_move_list
        Using = 'NotGreat_move_list'

    if num_OK_moves > 0:
        move_list = OK_move_list
        Using = 'OK_move_list'

    if num_Good_moves > 0:
        move_list = Good_move_list
        Using = 'Good_move_list'

    num_moves = len(move_list)
    print(f'Using {Using}')

    if num_moves > 0:

        # first get lowest max Y gap

        minygap = 10
        minygapowner = -1
        # for m in move_list:
        for m in range(0,num_moves):
            # print(f'm: {m}')
            ygap = GetMaxYGap(boards[m])
            if ygap < minygap:
                minygap = ygap
                minygapowner = m

        if minygapowner > -1:
            # print(f'min y gap is {minygapowner}')
            choice = minygapowner

        else:

            import random
            choice = random.randint(0,num_moves-1)

        # print(f'{num_Good_moves} good moves, {num_OK_moves} ok moves, {num_NotGreat_moves} not great moves, {num_InitialBlock_moves} initial blocks')

        # print(f'Using {Using}, choice is {choice}') 
        # print(f'Move is {move_list[choice]}')
        
        print('After')
        bs.ShowBoard(boards[move_list[choice]])
        return boards[move_list[choice]]
    else:
        print('No Move')
        return board

    # end = time.time()
    # print(f'Finish Elapsed time: {end - startstart} seconds')