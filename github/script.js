document.addEventListener("DOMContentLoaded", function() {
    const startButton = document.getElementById("startButton");
    const usernameInput = document.getElementById("username");
    const registrationDiv = document.getElementById("registration");
    const gameModesDiv = document.getElementById("gameModes");
    let morseInput = "";
    let answerTimeout;
    

    // Handle user registration
    startButton.addEventListener("click", function() {
        const username = usernameInput.value.trim();
        if (username === "") {
            alert("Please enter a username.");
            return;
        }

        fetch("/save-username", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Username saved successfully:", username);
                registrationDiv.style.display = "none"; // Hide registration
                gameModesDiv.style.display = "block"; // Show game modes
            } else {
                alert("Failed to save username: " + (data.error || "Unknown error"));
            }
        })
        .catch(error => console.error("Error:", error));
    });

    // Fetch username from the server
    fetch("/get-username")
        .then(response => response.json())
        .then(data => {
            if (data.username) {
                document.getElementById("usernameDisplay").textContent = data.username;
            }
        })
        .catch(error => console.error("Error fetching username:", error));

    // Fetch game state from the server
// Fetch game state from the server
function fetchGameState() {
    fetch("/api/game1-state")
        .then(response => response.json())
        .then(data => {
            console.log("Received game state:", data);

            // ✅ Ensure UI updates correctly
            document.getElementById("level").textContent = data.level ?? "1";
            document.getElementById("score").textContent = data.score ?? "0";
            document.getElementById("attempts").textContent = data.attempts ?? "5"; // ✅ Fix attempts sync

            document.getElementById("morseSequence").textContent = data.morse_sequence ?? "...";
            document.getElementById("hint").textContent = data.hint ?? "No hint available";

            // ✅ Handle game over state properly
            if (data.attempts <= 0) {
                document.getElementById("message").textContent = "Game Over! No more attempts.";
                document.getElementById("submitButton").disabled = true;
                document.getElementById("morseInput").disabled = true; 
            }
        })
        .catch(error => console.error("Error fetching game state:", error));
}  // This closing brace was missing


    // Fetch initial game state
    fetchGameState();

    // Add Morse code input
    window.addMorse = function(symbol) {
        morseInput += symbol;
        document.getElementById("morseInputDisplay").textContent = morseInput;
    };

    // Clear Morse code input
    window.clearMorse = function() {
        morseInput = "";
        document.getElementById("morseInputDisplay").textContent = "---";
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

            // Update UI with game state
            document.getElementById("message").textContent = data.message;
            document.getElementById("score").textContent = data.score;
            document.getElementById("level").textContent = data.level;
            document.getElementById("attempts").textContent = data.attempts;

            if (data.correct) {
                document.getElementById("message").textContent = "Correct! Next level.";
                fetchGameState(); // Refresh new sequence
            } else {
                document.getElementById("message").textContent = "Incorrect! Try again.";
            }

            // Disable input if game over
            if (data.game_over) {
    document.getElementById("message").textContent = "Game Over! No more attempts.";
    document.getElementById("submitButton").disabled = true;
    document.getElementById("morseInput").disabled = true;
}


            clearMorse();
        })
        .catch(error => console.error("Error submitting Morse code:", error));
    };

    // Quit game - Save and Redirect to results
    window.quitGame = function() {
        fetch("/save-game1-progress", { method: "POST" })
            .then(() => {
                window.location.href = "result.html";
            })
            .catch(error => console.error("Error saving game progress:", error));
    };

    // 🔥 Keyboard Input Support
    document.addEventListener("keydown", function(event) {
        if (event.key === ".") {
            addMorse(".");
        } else if (event.key === "_") {
            addMorse("_");
        } else if (event.key === " ") {
            addMorse("/"); // Corrected space handling
        } else if (event.key === "Backspace") {
            morseInput = morseInput.slice(0, -1);
            document.getElementById("morseInputDisplay").textContent = morseInput;
        } else if (event.key === "Enter") {
            submitMorseCode();
        }
    });
});

// ✅ Global function for starting different game modes
function startGame(mode) {
    console.log("Game mode selected:", mode);

    if (mode === "memory") {
        window.location.href = "/game1";  
    } else if (mode === "riddle") {
        window.location.href = "/game2";
    } else if (mode === "quiz") {
        window.location.href = "/game3";
    } else {
        alert("Invalid game mode selected.");
    }
}


