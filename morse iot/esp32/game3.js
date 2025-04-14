document.addEventListener("DOMContentLoaded", function () {
    let morseInput = "";
    let attempts = 5; // Default attempts (syncs with server)

    // Fetch username from the server and display it
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
        fetch("/api/game3-state")
            .then(response => response.json())
            .then(data => {
                console.log("Received game state:", data);

                document.getElementById("level").textContent = data.level ?? "1";
                document.getElementById("score").textContent = data.score ?? "0";
                document.getElementById("attempts").textContent = data.attempts ?? "5";

                attempts = data.attempts; // Sync attempts with server

                // Update Hint (Riddle)
                document.getElementById("hint").textContent = data.hint ?? "No hint available";

                checkGameOver(); // Check if game is over
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

        fetch("/submit-game3-morse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: morseInput })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Morse submission response:", data);

            // Update UI elements
            document.getElementById("message").textContent = data.message;
            document.getElementById("score").textContent = data.score;
            document.getElementById("level").textContent = data.level;
            document.getElementById("attempts").textContent = data.attempts;

            // ✅ Check if game is over
            if (data.game_over || data.attempts <= 0) {
                document.getElementById("message").textContent = "Game Over! No more attempts.";
                document.getElementById("submitButton").disabled = true;  // Disable submit button
                document.getElementById("morseInput").disabled = true;    // Disable Morse input
                return;  // Stop execution
            }

            // ✅ If correct answer, fetch new state

            if (data.correct) {
                document.getElementById("message").textContent = "Correct! Next level.";
                setTimeout(fetchGameState, 500); // Delay fetching to allow UI update
            } else {
                document.getElementById("message").textContent = "Incorrect! You lost 5 points.";
                updateScore(-5); // Deduct 5 points for incorrect answer
                
                let scoreElement = document.getElementById("score");
                let currentScore = parseInt(scoreElement.textContent) || 0;
                currentScore = Math.max(0, currentScore - 5); // Prevent negative score
                scoreElement.textContent = currentScore;
            }

            clearMorse();  // Reset Morse input
        })
        .catch(error => console.error("Error submitting Morse code:", error));
    };

    // Quit game - Save and Redirect to results


window.quitGame = function () {
    const username = document.getElementById("username").textContent.trim();
    const score = parseInt(document.getElementById("score").textContent.trim(), 10);

    if (!username) {
        console.error("❌ Error: Username is missing!");
        alert("Error: No username found.");
        return;
    }


fetch("/save-game3-progress", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: username, score: score })
})
.then(response => response.text())  // Get raw text response
.then(text => {
    console.log("🔍 Server response (raw):", text);  // Log raw response

    let data;
    try {
        data = JSON.parse(text);  // Try to parse JSON
    } catch (error) {
        console.error("❌ JSON Parse Error:", error);
        alert("Server returned invalid response! Check console.");
        return;
    }

    if (data.success) {
        console.log("✅ Game progress saved!");
        window.location.href = "result.html"; // Redirect after saving
    } else {
        console.error("❌ Error saving progress:", data.error);
        alert("Error saving progress: " + data.error);
    }
})
.catch(error => console.error("❌ Network error:", error));
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

// gpio part
// Add to game1.js, game2.js, game3.js
const ws = new WebSocket(`ws://${window.location.hostname}/ws`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === "input") {
        document.getElementById("morseInputDisplay").textContent = data.data;
    }
};