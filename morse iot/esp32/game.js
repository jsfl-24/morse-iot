document.addEventListener("DOMContentLoaded", function () {
    let morseInput = "";

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
    fetch("/api/game1-state")
        .then(response => response.json())
        .then(data => {
            document.getElementById("level").textContent = data.level;
            document.getElementById("score").textContent = data.score;
            document.getElementById("attempts").textContent = data.attempts;
            document.getElementById("morseSequence").textContent = data.sequence;
        })
        .catch(error => console.error("Error fetching game state:", error));
        
    fetch('/riddles.json')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error loading riddles:', error));


    // Add Morse code input
    window.addMorse = function (symbol) {
        morseInput += symbol;
        document.getElementById("morseInputDisplay").textContent = morseInput;
    };

    // Clear Morse code input
    window.clearMorse = function () {
        morseInput = "";
        document.getElementById("morseInputDisplay").textContent = "---";
    };

    // Submit Morse code
    window.submitMorseCode = function () {
        fetch("/submit-morse", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: morseInput })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").textContent = data.message;
            if (data.correct) {
                document.getElementById("score").textContent = data.score;
                document.getElementById("level").textContent = data.level;
            } else {
                document.getElementById("attempts").textContent = data.attempts;
            }
            clearMorse();
        })
        .catch(error => console.error("Error submitting Morse code:", error));
    };

    // Quit game
    window.quitGame = function () {
        window.location.href = "/";
    };

function fetchKeyPress() {
    fetch("http://192.168.1.3:81/keypress")  // Change IP as needed
        .then(response => response.json())
        .then(data => {
            if (data.keypress) {
                let inputField = document.getElementById("morseInput");
                if (inputField) {
                    inputField.value += data.keypress;  // Add key to input
                }
            }
        })
        .catch(error => console.error("AJAX Error:", error));
}

// Polling every 300ms
setInterval(fetchKeyPress, 300);

});
