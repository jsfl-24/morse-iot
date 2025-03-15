document.addEventListener("DOMContentLoaded", () => {
    let currentUsername = "";

    document.getElementById("startButton").addEventListener("click", registerUser);
    
    function registerUser() {
        let username = document.getElementById("username").value.trim();
        if (!username) {
            alert("Please enter a valid username.");
            return;
        }

        fetch("/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: username })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "User Registered") {
                currentUsername = username;
                document.getElementById("registration").classList.add("hidden");
                document.getElementById("gameModes").classList.remove("hidden");
            } else {
                alert("Failed to register. Try again.");
            }
        })
        .catch(error => {
            console.error("Error registering user:", error);
            alert("Server error. Try again later.");
        });
    }

    function startGame(mode) {
        fetch("/start_game", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: mode, username: currentUsername })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("gameModes").classList.add("hidden");
            document.getElementById("gameArea").classList.remove("hidden");
            updateGameUI(data);
        })
        .catch(error => console.error("Error starting game:", error));
    }

    function sendInput(input) {
        fetch("/input", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: input })
        })
        .then(response => response.json())
        .then(data => updateGameUI(data))
        .catch(error => console.error("Error sending input:", error));
    }

    function updateGameUI(data) {
        document.getElementById("level").innerText = data.level;
        document.getElementById("score").innerText = data.score;
        document.getElementById("attempts").innerText = data.attempts;
        
        let hintElement = document.getElementById("hint");
        if (data.hint) {
            hintElement.innerText = data.hint;
            hintElement.classList.remove("hidden");
            setTimeout(() => hintElement.classList.add("hidden"), 5000);
        }

        if (data.leaderboard) {
            updateLeaderboard(data.leaderboard);
        }
    }

    function updateLeaderboard(leaderboard) {
        let leaderboardElement = document.getElementById("leaderboard");
        let leaderboardList = document.getElementById("leaderboardList");
        leaderboardList.innerHTML = "";
        leaderboard.forEach(entry => {
            let listItem = document.createElement("li");
            listItem.innerText = `${entry.username}: ${entry.score}`;
            leaderboardList.appendChild(listItem);
        });
        leaderboardElement.classList.remove("hidden");
    }

    function fetchGameData() {
        fetch("/game_data")
        .then(response => response.json())
        .then(data => updateGameUI(data))
        .catch(error => console.error("Error fetching game data:", error));
    }

    setInterval(fetchGameData, 2000);
});
