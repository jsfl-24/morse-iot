// script.js

// Variables
let currentInput = "";
let currentPuzzle = "";

// Handle Registration
document.getElementById('registerForm').addEventListener('submit', (event) => {
  event.preventDefault();

  const playerName = document.getElementById('playerNameInput').value;
  const playerEmail = document.getElementById('playerEmailInput').value;

  fetch('http://your-webserver-ip/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: playerName, email: playerEmail }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        document.getElementById('registrationMessage').textContent = 'Registration successful!';
        startGame(data.player); // Pass player data to the game
      } else {
        document.getElementById('registrationMessage').textContent = 'Error: ' + data.message;
      }
    });
});

// Start the game
function startGame(player) {
  document.getElementById('registration').style.display = 'none';
  document.getElementById('game').style.display = 'block';
  document.getElementById('welcomeMessage').textContent = `Welcome, ${player.name}! Your score: ${player.score}`;
  loadPuzzle();
}

// Load a new puzzle
function loadPuzzle() {
  fetch('http://your-webserver-ip/new-puzzle')
    .then(response => response.json())
    .then(data => {
      currentPuzzle = data.puzzle; // Example: "SOS"
      document.getElementById('morsePuzzle').textContent = data.morse; // Example: "... --- ..."
    });
}

// Add input
function submitInput(char) {
  currentInput += char;
  document.getElementById('gameFeedback').textContent = `Your input: ${currentInput}`;
}

// Submit answer
function submitAnswer() {
  fetch('http://your-webserver-ip/submit-answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ puzzle: currentPuzzle, input: currentInput }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.correct) {
        document.getElementById('gameFeedback').textContent = 'Correct! Loading next puzzle...';
        loadPuzzle();
      } else {
        document.getElementById('gameFeedback').textContent = 'Incorrect! Try again.';
      }
      currentInput = ""; // Reset input
    });
}

// Load leaderboard
function loadLeaderboard() {
  fetch('http://your-webserver-ip/leaderboard')
    .then(response => response.json())
    .then(data => {
      const leaderboardBody = document.getElementById('leaderboardBody');
      leaderboardBody.innerHTML = '';

      data.forEach((player, index) => {
        const row = `
          <tr>
            <td>${index + 1}</td>
            <td>${player.name}</td>
            <td>${player.score}</td>
          </tr>
        `;
        leaderboardBody.innerHTML += row;
      });
    });
}

// Initial load
loadLeaderboard();
