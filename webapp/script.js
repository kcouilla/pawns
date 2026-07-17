const boardEl = document.getElementById('board');
const statusEl = document.getElementById('status');
const saveStartBtn = document.getElementById('saveStartBtn');
const newGameBtn = document.getElementById('newGameBtn');

let state = {
  board: [],
  history: [],
  legalMoves: [],
  gameId: 0,
  queenTurn: true,
  gameOver: false,
  winner: null,
};

async function api(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
  return res.json();
}

function isLegal(row, col) {
  return state.legalMoves.some(([r, c]) => r === row && c === col);
}

function render() {
  boardEl.innerHTML = '';
  for (let row = 0; row < 8; row++) {
    for (let col = 0; col < 8; col++) {
      const square = document.createElement('div');
      const light = (row + col) % 2 === 0;
      square.className = 'square ' + (light ? 'light' : 'dark');

      const value = state.board[row][col];
      if (value >= 1 && value <= 4) {
        const piece = document.createElement('div');
        piece.className = 'piece pawn';
        square.appendChild(piece);
      } else if (value === 5) {
        const piece = document.createElement('div');
        piece.className = 'piece queen';
        square.appendChild(piece);
      }

      if (state.queenTurn && !state.gameOver && isLegal(row, col)) {
        square.classList.add('legal');
        square.addEventListener('click', () => onSquareClick(row, col));
      }

      boardEl.appendChild(square);
    }
  }

  if (state.gameOver) {
    statusEl.textContent = `Game over - winner is ${state.winner}`;
    newGameBtn.textContent = 'Play Again';
  } else if (state.queenTurn) {
    statusEl.textContent = 'Your move';
    newGameBtn.textContent = 'New Game';
  } else {
    statusEl.textContent = 'Thinking...';
    newGameBtn.textContent = 'New Game';
  }
}

async function onSquareClick(row, col) {
  if (!state.queenTurn || state.gameOver) return;

  const data = await api('/api/queen-move', {
    board: state.board,
    history: state.history,
    to: [row, col],
    gameId: state.gameId,
  });

  if (!data.ok) {
    return;
  }

  state.board = data.board;
  state.history = data.history;
  state.gameOver = data.gameOver;
  state.winner = data.winner;
  state.legalMoves = data.legalMoves;
  state.queenTurn = false;
  render();

  if (!state.gameOver) {
    setTimeout(doComputerMove, 300);
  }
}

async function doComputerMove() {
  const data = await api('/api/computer-move', {
    board: state.board,
    history: state.history,
    gameId: state.gameId,
  });

  state.board = data.board;
  state.history = data.history;
  state.gameOver = data.gameOver;
  state.winner = data.winner;
  state.legalMoves = data.legalMoves;
  state.queenTurn = true;
  render();
}

async function newGame() {
  const data = await api('/api/new-game');
  state = {
    board: data.board,
    history: data.history,
    legalMoves: data.legalMoves,
    gameId: data.gameId,
    queenTurn: true,
    gameOver: false,
    winner: null,
  };
  render();
}

saveStartBtn.addEventListener('click', async () => {
  await api('/api/save-start', { board: state.board });
  statusEl.textContent = 'Start position saved';
  setTimeout(render, 1000);
});

newGameBtn.addEventListener('click', newGame);

newGame();
