from microdot import Microdot, send_file, Response
import wifi
import ujson
import os
import random
import gpio

app = Microdot()

# Connect to Wi-Fi
ip_address = wifi.connect()
if ip_address:
    print(f"Web server running at http://{ip_address}")
    
# Placeholder game state
game1_state = {
    "level": 1,
    "score": 0,
    "attempts": 5,
    "morse_sequence": "...-.-",  # Example Morse sequence for Memory Game
}
    
game2_state = {
    "level": 1,
    "score": 0,
    "attempts": 5,
    "correct_morse": "",  # To store the correct Morse code of the answer
    "answer": "",  # Correct answer in text
    "hint": ""  # Hint to be displayed
}

game3_state = {
    "level": 1,
    "score": 0,
    "attempts": 5,
    "correct_morse": "",  # To store the correct Morse code of the answer
    "answer": "",  # Correct answer in text
    "hint": ""  # Hint to be displayed
}


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
    


@app.route("/get-username", methods=["GET"])
def get_username():
    username = session.get("username")
    if not username:
        return jsonify({"error": "No username found"}), 401

    return jsonify({"username": username})
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
    try:
        if file_exists("current_user.txt"):
            with open("current_user.txt", "r") as f:
                username = f.read().strip()
                if username:
                    return Response(ujson.dumps({"username": username}), headers={"Content-Type": "application/json"})

    except Exception as e:
        print("Error reading current_user.txt:", e)

    return Response(ujson.dumps({"username": None}), headers={"Content-Type": "application/json"})


import random

# Load riddle from JSON file
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


# Load CSE Quiz questions from JSON file
def load_cse_quiz():
    filename = "cseq.json"
    if file_exists(filename):
        with open(filename, "r") as f:
            try:
                return ujson.load(f)
            except ValueError:
                print("Error: Could not parse cseq.json")
    return []

cse_quiz = load_cse_quiz()



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


@app.route('/api/game2-state')
def get_game2_state(request):
    global game2_state

    if not riddles:
        return Response(ujson.dumps({"error": "No riddles available"}), headers={"Content-Type": "application/json"})

    # Select a random riddle for the current level
    level = game2_state["level"]
    filtered_riddles = [r for r in riddles if r["level"] == level]

    if not filtered_riddles:
        filtered_riddles = riddles  # If no specific level, use any riddle

    riddle = random.choice(filtered_riddles)

    # Update game state with new riddle
    game2_state["correct_morse"] = riddle["morse"]
    game2_state["answer"] = riddle["answer"]
    game2_state["hint"] = riddle["hint"]

    return Response(ujson.dumps({
        "level": game2_state["level"],
        "score": game2_state["score"],
        "attempts": game2_state["attempts"],
        "hint": game2_state["hint"]  # Only showing the hint in Game 2
    }), headers={"Content-Type": "application/json"})


@app.route('/api/game3-state')
def get_game3_state(request):
    global game3_state

    if not cse_quiz:
        return Response(ujson.dumps({"error": "No cse_quiz available"}), headers={"Content-Type": "application/json"})

    # Select a random riddle for the current level
    level = game3_state["level"]
    filtered_cse_quiz = [r for r in cse_quiz if r["level"] == level]

    if not filtered_cse_quiz:
        filtered_cse_quiz = cse_quiz  # If no specific level, use any riddle

    riddle = random.choice(filtered_cse_quiz)

    # Update game state with new riddle
    game3_state["correct_morse"] = riddle["morse"]
    game3_state["answer"] = riddle["answer"]
    game3_state["hint"] = riddle["hint"]

    return Response(ujson.dumps({
        "level": game3_state["level"],
        "score": game3_state["score"],
        "attempts": game3_state["attempts"],
        "hint": game3_state["hint"]  # Only showing the hint in Game 2
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
    

@app.route('/submit-game2-morse', methods=['POST'])
def submit_game2_morse(request):
    global game2_state

    if game2_state["attempts"] <= 0:
        return Response(ujson.dumps({
            "correct": False,
            "message": "Game Over! No attempts left.",
            "score": game2_state["score"],
            "level": game2_state["level"],
            "attempts": game2_state["attempts"],
            "game_over": True
        }), headers={"Content-Type": "application/json"})

    try:
        data = request.json
        user_input = data.get("input", "").strip()

        if user_input == game2_state["correct_morse"]:
            game2_state["score"] += 10
            game2_state["level"] += 1
            game2_state["attempts"] = 5  # Reset attempts for next level
            correct = True
            message = "Correct! Moving to next level."
            game_over = False
        else:
            game2_state["attempts"] -= 1
            game2_state["score"] = max(0, game2_state["score"] - 5)  # Reduce score on incorrect answer
            correct = False
            message = "Incorrect! Try again."
            game_over = game2_state["attempts"] <= 0

        return Response(ujson.dumps({
            "correct": correct,
            "message": message,
            "score": game2_state["score"],
            "level": game2_state["level"],
            "attempts": game2_state["attempts"],
            "game_over": game_over
        }), headers={"Content-Type": "application/json"})

    except Exception as e:
        return Response(ujson.dumps({"success": False, "error": str(e)}), headers={"Content-Type": "application/json"})


@app.route('/submit-game3-morse', methods=['POST'])
def submit_game3_morse(request):
    global game3_state

    if game3_state["attempts"] <= 0:
        return Response(ujson.dumps({
            "correct": False,
            "message": "Game Over! No attempts left.",
            "score": game3_state["score"],
            "level": game3_state["level"],
            "attempts": game3_state["attempts"],
            "game_over": True
        }), headers={"Content-Type": "application/json"})

    try:
        data = request.json
        user_input = data.get("input", "").strip()

        if user_input == game3_state["correct_morse"]:
            game3_state["score"] += 10
            game3_state["level"] += 1
            game3_state["attempts"] = 5  # Reset attempts for next level
            correct = True
            message = "Correct! Moving to next level."
            game_over = False
        else:
            game3_state["attempts"] -= 1
            game3_state["score"] = max(0, game3_state["score"] - 5)  # Reduce score on incorrect answer
            correct = False
            message = "Incorrect! Try again."
            game_over = game3_state["attempts"] <= 0

        return Response(ujson.dumps({
            "correct": correct,
            "message": message,
            "score": game3_state["score"],
            "level": game3_state["level"],
            "attempts": game3_state["attempts"],
            "game_over": game_over
        }), headers={"Content-Type": "application/json"})

    except Exception as e:
        return Response(ujson.dumps({"success": False, "error": str(e)}), headers={"Content-Type": "application/json"})


import json

def update_score(username, points):
    try:
        with open('userdata.json', 'r') as file:
            users = json.load(file)

        if username in users:
            users[username]['score'] += points  # Update score
        else:
            users[username] = {'score': points}  # Create new entry if missing

        with open('userdata.json', 'w') as file:
            json.dump(users, file, indent=4)

    except Exception as e:
        print(f"Error updating score: {e}")



import json

USERDATA_FILE = "userdata.json"


@app.route("/save-game1-progress", methods=["POST"])
def save_game1_progress(request):
    try:
        data = request.json
        if not data:
            return Response(ujson.dumps({"success": False, "error": "No data received"}), headers={"Content-Type": "application/json"})

        username = data.get("username", "").strip()
        score = data.get("score")

        if not username or score is None:
            return Response(ujson.dumps({"success": False, "error": "Missing username or score"}), headers={"Content-Type": "application/json"})

        filename = "userdata.json"

        # Ensure file exists before reading
        if not file_exists(filename):
            users = {}
        else:
            with open(filename, "r") as f:
                try:
                    users = ujson.load(f)
                    if not isinstance(users, dict):
                        users = {}
                except ValueError:
                    users = {}

        # Ensure user exists in the dictionary
        if username not in users:
            users[username] = {"memory_mode": 0, "riddle_mode": 0, "cse_mode": 0}

        # Update score only if it's higher than the stored one
        users[username]["memory_mode"] = max(users[username]["memory_mode"], score)

        # Save back to file
        with open(filename, "w") as f:
            ujson.dump(users, f)

        return Response(ujson.dumps({"success": True}), headers={"Content-Type": "application/json"})

    except Exception as e:
        print("❌ Error in save-game1-progress:", str(e))
        return Response(ujson.dumps({"success": False, "error": str(e)}), headers={"Content-Type": "application/json"})


@app.route("/save-game2-progress", methods=["POST"])
def save_game2_progress(request):
    try:
        data = request.json
        if not data:
            return Response(ujson.dumps({"success": False, "error": "No data received"}), headers={"Content-Type": "application/json"})

        username = data.get("username", "").strip()
        score = data.get("score")

        if not username or score is None:
            return Response(ujson.dumps({"success": False, "error": "Missing username or score"}), headers={"Content-Type": "application/json"})

        filename = "userdata.json"

        # Ensure file exists before reading
        if not file_exists(filename):
            users = {}
        else:
            with open(filename, "r") as f:
                try:
                    users = ujson.load(f)
                    if not isinstance(users, dict):
                        users = {}
                except ValueError:
                    users = {}

        # Ensure user exists in the dictionary
        if username not in users:
            users[username] = {"memory_mode": 0, "riddle_mode": 0, "cse_mode": 0}

        # Update score only if it's higher than the stored one
        users[username]["riddle_mode"] = max(users[username]["riddle_mode"], score)

        # Save back to file
        with open(filename, "w") as f:
            ujson.dump(users, f)

        return Response(ujson.dumps({"success": True}), headers={"Content-Type": "application/json"})

    except Exception as e:
        print("❌ Error in save-game2-progress:", str(e))
        return Response(ujson.dumps({"success": False, "error": str(e)}), headers={"Content-Type": "application/json"})


@app.route("/save-game3-progress", methods=["POST"])
def save_game3_progress(request):
    try:
        data = request.json
        if not data:
            return Response(ujson.dumps({"success": False, "error": "No data received"}), headers={"Content-Type": "application/json"})

        username = data.get("username", "").strip()
        score = data.get("score")

        if not username or score is None:
            return Response(ujson.dumps({"success": False, "error": "Missing username or score"}), headers={"Content-Type": "application/json"})

        filename = "userdata.json"

        # Ensure file exists before reading
        if not file_exists(filename):
            users = {}
        else:
            with open(filename, "r") as f:
                try:
                    users = ujson.load(f)
                    if not isinstance(users, dict):
                        users = {}
                except ValueError:
                    users = {}

        # Ensure user exists in the dictionary
        if username not in users:
            users[username] = {"memory_mode": 0, "riddle_mode": 0, "cse_mode": 0}

        # Update score only if it's higher than the stored one
        users[username]["riddle_mode"] = max(users[username]["riddle_mode"], score)

        # Save back to file
        with open(filename, "w") as f:
            ujson.dump(users, f)

        return Response(ujson.dumps({"success": True}), headers={"Content-Type": "application/json"})

    except Exception as e:
        print("❌ Error in save-game3-progress:", str(e))
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
                        "cse_mode": scores.get("cse_mode", 0),
                        "total_score": scores.get("memory_mode", 0) +
                                       scores.get("riddle_mode", 0) +
                                       scores.get("cse_mode", 0)
                    }
                    for username, scores in users.items()
                ]

                # Sort by highest total score
                leaderboard.sort(key=lambda x: x["total_score"], reverse=True)

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

@app.route('/game2')
def game2(request):
    return send_file('game2.html', content_type='text/html')

@app.route('/game2.js')
def game2_script(request):
    return send_file('game2.js', content_type='application/javascript')

@app.route('/game3')
def game3(request):
    return send_file('game3.html', content_type='text/html')

@app.route('/game3.js')
def game3_script(request):
    return send_file('game3.js', content_type='application/javascript')


import os

if file_exists("userdata.json"):
    with open("userdata.json", "r") as f:
        print(f.read())  # Print stored user data
else:
    print("userdata.json does not exist.")


#gpio part
from microdot import Microdot, request, Response
import json

app = Microdot()

# Global variable to store Morse input
morse_input = ""

@app.route("/api/morse-input", methods=["POST"])
def receive_morse_input(request):
    global morse_input
    data = request.json

    if not data or "input" not in data:
        return Response(json.dumps({"error": "Invalid request"}), content_type="application/json", status=400)

    symbol = data["input"]

    if symbol == "clear":
        morse_input = ""  # Clear input
    elif symbol == "submit":
        result = process_morse_submission(morse_input)  # Process input
        morse_input = ""  # Reset after submission
        return Response(json.dumps(result), content_type="application/json")
    else:
        morse_input += symbol  # Append Morse input

    return Response(json.dumps({"morse": morse_input}), content_type="application/json")

def process_morse_submission(morse_code):
    """
    Validate Morse input against the correct answer and update the game state.
    """
    try:
        with open("cseq.json", "r") as file:
            data = json.load(file)
    except Exception as e:
        return {"result": "error", "message": "Error reading question data", "score": 0}

    correct_answer = data.get("current_answer", "").strip()

    if morse_code.strip() == correct_answer:
        return {"result": "correct", "message": "Correct!", "score": 10}
    else:
        return {"result": "incorrect", "message": "Incorrect! -5 points", "score": -5}

@app.route("/api/get-morse", methods=["GET"])
def get_morse_input(request):
    """
    API to fetch current Morse input for AJAX updates.
    """
    return Response(json.dumps({"morse": morse_input}), content_type="application/json")

if __name__ == "__main__":
    app.run(debug=True)


# Start the web server
app.run(port=80)