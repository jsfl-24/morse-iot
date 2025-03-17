from microdot import Microdot, send_file, Response
import wifi
import ujson
import os

app = Microdot()

# Connect to Wi-Fi
ip_address = wifi.connect()
if ip_address:
    print(f"Web server running at http://{ip_address}")

# Serve the main webpage
@app.route('/')
def index(request):
    return send_file('index.html', content_type='text/html')

# Serve JavaScript files
@app.route('/script.js')
def script(request):
    return send_file('script.js', content_type='application/javascript')

# API Endpoint to get game state
@app.route('/api/game-state')
def game_state(request):
    return Response(ujson.dumps({"status": "running", "message": "Game server is active"}), headers={"Content-Type": "application/json"})

# Function to check if a file exists in MicroPython
def file_exists(filename):
    try:
        os.stat(filename)  # If the file exists, stat() will succeed
        return True
    except OSError:
        return False  # If the file doesn't exist, stat() will raise an error

# Save username to userdata.json

@app.route('/save-username', methods=['POST'])
def save_username(request):
    try:
        print("Received request to save username")
        data = request.json
        print("Received data:", data)

        username = data.get("username", "").strip()

        if not username:
            print("Error: Invalid username")
            return Response(ujson.dumps({"success": False, "error": "Invalid username"}), headers={"Content-Type": "application/json"})

        filename = "userdata.json"

        # Try loading existing data
        if file_exists(filename):
            with open(filename, "r") as f:
                try:
                    users = ujson.load(f)
                    if not isinstance(users, dict):  # Ensure it's a dictionary
                        print("Warning: userdata.json was not a dictionary, resetting to empty dict")
                        users = {}
                except ValueError:
                    print("Error: userdata.json is corrupted, resetting file")
                    users = {}
        else:
            users = {}

        # Ensure username is stored properly with an initial score structure
        if username not in users:
            users[username] = {"memory_mode": 0, "riddle_mode": 0, "cse_mode": 0}

        # Save back to file
        with open(filename, "w") as f:
            ujson.dump(users, f)

        print(f"Username '{username}' saved successfully")
        return Response(ujson.dumps({"success": True}), headers={"Content-Type": "application/json"})

    except Exception as e:
        print("Error:", str(e))
        return Response(ujson.dumps({"success": False, "error": str(e)}), headers={"Content-Type": "application/json"})
# Serve the Memory Game page
@app.route('/game1')
def game1(request):
    return send_file('game1.html', content_type='text/html')

# Serve the Memory Game script
@app.route('/game1.js')
def game1_script(request):
    return send_file('game1.js', content_type='application/javascript')

@app.route('/get-username')
def get_username(request):
    filename = "userdata.json"

    if file_exists(filename):
        with open(filename, "r") as f:
            try:
                users = ujson.load(f)
                if isinstance(users, list) and users:
                    return Response(ujson.dumps({"username": users[-1]}), headers={"Content-Type": "application/json"})
            except ValueError:
                pass  # Handle JSON errors gracefully

    return Response(ujson.dumps({"username": None}), headers={"Content-Type": "application/json"})

# Placeholder game state
game1_state = {
    "level": 1,
    "score": 0,
    "attempts": 5,
    "morse_sequence": "...-.-",  # Example Morse sequence for Memory Game
}

import random

# Load riddles from JSON file
def load_riddles():
    filename = "riddles.json"
    if file_exists(filename):
        with open(filename, "r") as f:
            try:
                return ujson.load(f)
            except ValueError:
                print("Error: Could not parse riddles.json")
    return []

riddles = load_riddles()

@app.route('/api/game1-state')
def get_game1_state(request):
    global game1_state

    if not riddles:
        return Response(ujson.dumps({"error": "No riddles available"}), headers={"Content-Type": "application/json"})

    # Select a random riddle based on the level
    level = game1_state["level"]
    filtered_riddles = [r for r in riddles if r["level"] == level]

    if not filtered_riddles:
        filtered_riddles = riddles  # If no specific level, use any riddle

    riddle = random.choice(filtered_riddles)

    # Update game state with new riddle
    game1_state["morse_sequence"] = riddle["morse"]
    game1_state["answer"] = riddle["answer"]
    game1_state["hint"] = riddle["hint"]

    return Response(ujson.dumps({
        "level": game1_state["level"],
        "score": game1_state["score"],
        "attempts": game1_state["attempts"],
        "morse_sequence": game1_state["morse_sequence"],  # Morse version of the answer
        "answer": game1_state["answer"],  # Alphabetic answer (will be shown after 10s)
        "hint": game1_state["hint"]  # Hint shown always
    }), headers={"Content-Type": "application/json"})



@app.route('/submit-morse', methods=['POST'])
def submit_morse(request):
    global game1_state
    
    if game1_state["attempts"] <= 0:
        return Response(ujson.dumps({
            "correct": False,
            "message": "Game Over! No more attempts left.",
            "score": game1_state["score"],
            "level": game1_state["level"],
            "attempts": game1_state["attempts"],
            "game_over": True
        }), headers={"Content-Type": "application/json"})

    try:
        data = request.json
        user_input = data.get("input", "").strip()

        if user_input == game1_state["morse_sequence"]:
            game1_state["score"] += 10
            game1_state["level"] += 1
            game1_state["attempts"] = 5
            correct = True
            message = "Correct! Next level."
            game_over = False
        else:
            game1_state["attempts"] -= 1
            game1_state["score"] = max(0, game1_state["score"] - 5)

            correct = False
            message = "Incorrect. Try again."
            game_over = game1_state["attempts"] <= 0  # Set game over flag

        return Response(ujson.dumps({
            "correct": correct,
            "message": message,
            "score": game1_state["score"],
            "level": game1_state["level"],
            "attempts": game1_state["attempts"],
            "game_over": game_over
        }), headers={"Content-Type": "application/json"})

    except Exception as e:
        return Response(ujson.dumps({"success": False, "error": str(e)}), headers={"Content-Type": "application/json"})
    
    

@app.route('/api/leaderboard')
def get_leaderboard(request):
    filename = "userdata.json"

    if file_exists(filename):
        with open(filename, "r") as f:
            try:
                users = ujson.load(f)

                # Ensure the file contains a dictionary
                if not isinstance(users, dict):
                    return Response(ujson.dumps({"error": "Invalid leaderboard format"}), headers={"Content-Type": "application/json"})

                leaderboard = [
                    {
                        "username": username,
                        "memory_mode": scores.get("memory_mode", 0),
                        "riddle_mode": scores.get("riddle_mode", 0),
                        "cse_mode": scores.get("cse_mode", 0)
                    }
                    for username, scores in users.items()
                ]

                # Sort by highest memory_mode score
                leaderboard.sort(key=lambda x: x["memory_mode"], reverse=True)

                return Response(ujson.dumps(leaderboard), headers={"Content-Type": "application/json"})

            except ValueError:
                return Response(ujson.dumps({"error": "Error reading leaderboard"}), headers={"Content-Type": "application/json"})

    return Response(ujson.dumps([]), headers={"Content-Type": "application/json"})

    
# Serve the result leaderboard page
@app.route('/result')
def result_page(request):
    return send_file('result.html', content_type='text/html')

# Serve the Memory Game page
@app.route('/game1')
def game1(request):
    return send_file('game1.html', content_type='text/html')

@app.route("/game1.js")
def serve_game1_js(request):
    return send_file("game1.js", content_type="application/javascript")

import os
print(os.listdir())


# Start the web server
app.run(port=80)


