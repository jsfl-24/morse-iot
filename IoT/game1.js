let currentLevel = 1;
let correctMorseCode = "";
let currentRiddle = {};

// Fetch a random riddle from the current level
function fetchRiddle() {
    fetch(`/get_riddle?level=${currentLevel}`)
        .then(response => response.json())
        .then(data => {
            if (!data.riddles || data.riddles.length === 0) {
                console.error("No riddles found for this level.");
                return;
            }

            // Pick a random riddle from the available list
            let randomIndex = Math.floor(Math.random() * data.riddles.length);
            currentRiddle = data.riddles[randomIndex];

            document.getElementById("riddle").innerText = currentRiddle.riddle;
            correctMorseCode = currentRiddle.morse;

            let morseHintElement = document.getElementById("morseHint");
            let alphabetHintElement = document.getElementById("alphabetHint");

            // Show Morse hint for 10 seconds
            morseHintElement.innerText = "Morse: " + correctMorseCode;
            alphabetHintElement.innerText = ""; // Clear alphabetic hint initially
            alphabetHintElement.classList.add("hidden");

            setTimeout(() => {
                morseHintElement.classList.add("hidden");
                alphabetHintElement.innerText = "Answer: " + currentRiddle.answer;
                alphabetHintElement.classList.remove("hidden");
            }, 10000);
        })
        .catch(error => console.error("Error fetching riddle:", error));
}

// Verify user input
function submitMorseCode() {
    let userInput = document.getElementById("morseInput").value.trim();
    let messageElement = document.getElementById("message");

    fetch("/check_morse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ morse: userInput })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("level").innerText = `|| ${data.level} ||`;
        document.getElementById("score").innerText = data.score;
        document.getElementById("attempts").innerText = data.attempts;

        messageElement.innerText = data.message;
        messageElement.className = data.success ? "text-green-400" : "text-red-400";

        // Reset input field
        document.getElementById("morseInput").value = "";

        if (data.success) {
            currentLevel = data.level;
            
            // Check if all levels are completed (Bonus level included)
            if (currentLevel > 5) {
                localStorage.setItem("finalScore", data.score);
                window.location.href = "results.html"; // Redirect to results page
                return;
            }

            fetchRiddle(); // Load the next riddle
        }

        // Handle Game Over
        if (data.attempts <= 0) {
            localStorage.setItem("finalScore", data.score);
            window.location.href = "results.html"; // Redirect to results page
        }
    })
    .catch(error => console.error("Error submitting Morse:", error));
}

// Fetch initial riddle on page load
document.addEventListener("DOMContentLoaded", fetchRiddle);
