import os
import sys
import time
from pathlib import Path

WEBAPP_DIR = Path(__file__).resolve().parent
PAWNS_ROOT = str(WEBAPP_DIR.parent)

# Eng_2.py resolves files/game.csv and files/game_moves.csv relative to the
# process cwd at import time, and needs the pawns root on sys.path to find
# basic_stuff.py. Under IIS/wfastcgi the worker's cwd is unpredictable, so
# fix both before importing game_logic (which imports Eng_2).
os.chdir(PAWNS_ROOT)
if PAWNS_ROOT not in sys.path:
    sys.path.insert(0, PAWNS_ROOT)

import numpy as np
from flask import Flask, jsonify, request

import game_logic as gl

app = Flask(__name__, static_folder=str(WEBAPP_DIR), static_url_path='')

patterns = np.asarray(gl.LoadPatterns('patterns.csv'))
ipatterns = gl.Load_I_Patterns('iboards.csv')


def board_to_list(board):
    return board.tolist()


def board_from_list(data):
    return np.array(data, dtype=int)


def log_move(history, game_id, winner):
    gl.SaveThisGame(history, len(history) - 1, game_id, winner or 'No one')


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/api/new-game', methods=['POST'])
def new_game():
    board = gl.initboard(False)
    return jsonify({
        'board': board_to_list(board),
        'legalMoves': gl.CalcHumanMove(board),
        'history': [board_to_list(board)],
        'gameId': int(time.time()),
    })


@app.route('/api/queen-move', methods=['POST'])
def queen_move():
    data = request.get_json()
    board = board_from_list(data['board'])
    history = data.get('history', [board_to_list(board)])
    game_id = data.get('gameId', 0)
    to_x, to_y = data['to']

    pos = gl.GetPositions(board)
    qposx, qposy = int(pos[0, 4]), int(pos[1, 4])

    legal = (
        0 <= to_x <= 7 and 0 <= to_y <= 7
        and ((to_x + to_y) % 2) == 0
        and abs(to_x - qposx) == 1
        and abs(to_y - qposy) == 1
        and board[to_x, to_y] == 0
    )

    if not legal:
        return jsonify({
            'ok': False,
            'board': board_to_list(board),
            'legalMoves': gl.CalcHumanMove(board),
        })

    board[qposx, qposy] = 0
    board[to_x, to_y] = 5

    new_history = history + [board_to_list(board)]
    game_over, winner = gl.get_game_status(board)
    log_move(new_history, game_id, winner)

    return jsonify({
        'ok': True,
        'board': board_to_list(board),
        'history': new_history,
        'gameOver': game_over,
        'winner': winner,
        'legalMoves': gl.CalcHumanMove(board) if game_over else [],
    })


@app.route('/api/computer-move', methods=['POST'])
def computer_move():
    data = request.get_json()
    board = board_from_list(data['board'])
    history = data.get('history', [board_to_list(board)])
    game_id = data.get('gameId', 0)

    nboard = gl.ComputerMove(board, patterns, ipatterns)

    new_history = history + [board_to_list(nboard)]
    game_over, winner = gl.get_game_status(nboard)
    log_move(new_history, game_id, winner)

    return jsonify({
        'board': board_to_list(nboard),
        'history': new_history,
        'gameOver': game_over,
        'winner': winner,
        'legalMoves': gl.CalcHumanMove(nboard) if not game_over else [],
    })


@app.route('/api/save-start', methods=['POST'])
def save_start():
    data = request.get_json()
    board = board_from_list(data['board'])
    gl.SaveStart(board)
    return jsonify({'ok': True})


if __name__ == '__main__':
    # use_reloader=False: the reloader re-execs python against a relative
    # path to this file, which breaks because we os.chdir() above.
    app.run(debug=True, use_reloader=False)
