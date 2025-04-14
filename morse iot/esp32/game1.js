document.addEventListener("DOMContentLoaded", function () {
    let morseInput = "";
    let answerTimeout;
    let attempts = 5; // Default attempts (syncs with server)

    // Fetch username from the server
    fetch("/get-username")
        .then(response => response.json())
        .then(data => {
            if (data.username) {
                document.getElementById("username").textContent = data.username;
            }
        })
        .catch(error => console.error("Error fetching username:", error));

    // Fetch game state from the server
    function fetchGameState() {
        fetch("/api/game1-state")
            .then(response => response.json())
            .then(data => {
                console.log("Received game state:", data);

                document.getElementById("level").textContent = data.level ?? "1";
                document.getElementById("score").textContent = data.score ?? "0";
                document.getElementById("attempts").textContent = data.attempts ?? "5";

                attempts = data.attempts; // Sync attempts with server

                // Update Morse sequence and hints
                document.getElementById("morseSequence").textContent = data.morse_sequence ?? "...";
                document.getElementById("hint").textContent = data.hint ?? "No hint available";

                checkGameOver(); // Check if game is over

                // Reveal answer after 10 seconds
                if (data.answer) {
                    clearTimeout(answerTimeout);
                    answerTimeout = setTimeout(() => {
                        document.getElementById("answerHint").textContent = data.answer;
                        document.getElementById("answerHint").classList.remove("hidden");
                    }, 10000);
                }
            })
            .catch(error => console.error("Error fetching game state:", error));
    }

    // Fetch initial game state
    fetchGameState();

    // Check if game is over (disable input)
    function checkGameOver() {
        if (attempts <= 0) {
            document.getElementById("message").textContent = "Game Over! No attempts left.";
            document.getElementById("morseInputDisplay").textContent = "GAME OVER";
            disableInput();
        }
    }

    // Disable input when the game is over
    function disableInput() {
        document.removeEventListener("keydown", handleKeyPress);
        document.querySelectorAll(".morse-button").forEach(button => button.disabled = true);
    }

    // Add Morse code input
    window.addMorse = function (symbol) {
        if (attempts > 0) { // Allow input only if attempts are left
            morseInput += symbol;
            document.getElementById("morseInputDisplay").textContent = morseInput;
        }
    };

    // Clear Morse code input
    window.clearMorse = function () {
        if (attempts > 0) {
            morseInput = "";
            document.getElementById("morseInputDisplay").textContent = "---";
        }
    };

    // Submit Morse code and update score
window.submitMorseCode = function() {
    if (morseInput.trim() === "") {
        alert("Please enter Morse code before submitting.");
        return;
    }

    fetch("/submit-morse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: morseInput })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Morse submission response:", data);

        document.getElementById("message").textContent = data.message;
        document.getElementById("score").textContent = data.score;
        document.getElementById("attempts").textContent = data.attempts;

        if (data.game_over) {
            document.getElementById("message").textContent = "Game Over! No more attempts.";
            document.getElementById("submitButton").disabled = true;
            document.getElementById("morseInput").disabled = true;
        }

        if (data.correct) {
            document.getElementById("message").textContent = "Correct! Next level.";
            setTimeout(fetchGameState, 500);
        } else {
            document.getElementById("message").textContent = "Incorrect! Try again.";
        }

        clearMorse();
    })
    .catch(error => console.error("Error submitting Morse code:", error));
};




    // Quit game - Save and Redirect to results
    window.quitGame = function () {
        fetch("/save-game1-progress", { method: "POST" })
            .then(() => {
                window.location.href = "result.html";
            })
            .catch(error => console.error("Error saving game progress:", error));
    };

    // 🔥 Keyboard Input Support
    function handleKeyPress(event) {
        if (attempts <= 0) return; // Prevent input if game is over

        if (event.key === ".") {
            addMorse(".");
            sendMorseUpdate(".");
        } else if (event.key === "_") {
            addMorse("_");
            sendMorseUpdate("_");
        } else if (event.key === " ") {
            addMorse(" / "); // Space between words in Morse
            sendMorseUpdate("/");
        } else if (event.key === "Backspace") {
            morseInput = morseInput.slice(0, -1);
            sendMorseUpdate("clear");
            document.getElementById("morseInputDisplay").textContent = morseInput;
        } else if (event.key === "Enter") {
            submitMorseCode();
            sendMorseUpdate("submit");
        }
    }

    document.addEventListener("keydown", handleKeyPress);
});

// ajax,gpio...
// Function to fetch and update Morse input from ESP32
function updateMorseDisplay() {
    fetch("/get_morse_input")  // API to get Morse input from ESP32
        .then(response => response.text())
        .then(data => {
            document.getElementById("morseDisplay").innerText = data;
        })
        .catch(err => console.error("Error fetching Morse input:", err));
}

// Function to check answer and display result
function checkMorseAnswer() {
    fetch("/check_morse_answer")  // API to check answer
        .then(response => response.json())
        .then(data => {
            document.getElementById("resultDisplay").innerText = data.result;
        })
        .catch(err => console.error("Error checking answer:", err));
}

// Periodically update Morse input display
setInterval(updateMorseDisplay, 1000);
