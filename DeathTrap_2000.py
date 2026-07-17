import pygame
import numpy as np
import sys
import time

from game_logic import (
    squares,
    Load_I_Patterns,
    LoadPatterns,
    ComputerMove,
    CalcHumanMove,
    GetPositions,
    SaveStart,
    SaveThisGame,
    initboard,
    verbose,
)

intColour1 = 'burlywood'
intColour2 = 'Black'

rectsize = 99
squaresize = 100
size = (800, 800)

moves = np.zeros((60, squares, squares), dtype=int)

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

try:
    KeepPlaying = True
    while KeepPlaying:
        KeepPlaying = mainx(0)
except:
    print("Error!", sys.exc_info()[0], "occurred.")
    import traceback
    traceback.print_exc()
