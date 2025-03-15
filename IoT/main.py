import network
import socket
import ujson as json
import os
from microdot import Microdot, Response

# WiFi Configuration
SSID = "Asianet"
PASSWORD = "04042012"

# JSON File Paths
USERDATA_FILE = "userdata.json"
RIDDLES_FILE = "riddles.json"

# Web Server Initialization
app = Microdot()
Response.default_content_type = 'application/json'

# Game State Variables
game_state = {
    "level": 1,
    "score": 0,
    "attempts": 5,
    "current_answer": "",
    "current_morse": ""
}

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Connected! IP:", wlan.ifconfig()[0])

# Load JSON Data
def load_json(filename):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading {filename}:", e)
        return {}

# Load Riddles
riddles_data = load_json(RIDDLES_FILE)

# Fetch Current Riddle
def get_riddle(level):
    level_key = f"level{level}"
    if level_key in riddles_data and riddles_data[level_key]:
        riddle = riddles_data[level_key][0]  # Get first riddle of the level
        game_state["current_answer"] = riddle["answer"]
        game_state["current_morse"] = riddle["morse"]
        return {"riddle": riddle["riddle"], "answer": riddle["answer"], "morse": riddle["morse"]}
    return {"riddle": "No more riddles!", "answer": "", "morse": ""}

# Validate Morse Code Input
def check_morse_code(input_morse):
    if input_morse == game_state["current_morse"]:
        game_state["score"] += 10
        game_state["level"] += 1
        game_state["attempts"] = 5
        message = "✅ Correct! Level Up!"
        success = True
    else:
        game_state["score"] -= 5
        game_state["attempts"] -= 1
        message = "❌ Incorrect! Try again!"
        success = False

    if game_state["attempts"] == 0:
        message = "💀 Game Over! Restarting..."
        game_state["level"] = 1
        game_state["score"] = 0
        game_state["attempts"] = 5

    next_riddle = get_riddle(game_state["level"])
    return {
        "message": message,
        "success": success,
        "level": game_state["level"],
        "score": game_state["score"],
        "attempts": game_state["attempts"],
        "riddle": next_riddle["riddle"],
        "answer": next_riddle["answer"],
        "morse": next_riddle["morse"]
    }

# Serve `index.html`
@app.route('/')
def serve_index(request):
    try:
        with open("index.html", "r") as file:
            return Response(file.read(), headers={"Content-Type": "text/html"})
    except:
        return Response("Error loading index.html", status=500)

# Serve `game1.html`
@app.route('/game1.html')
def serve_game1(request):
    try:
        with open("game1.html", "r") as file:
            return Response(file.read(), headers={"Content-Type": "text/html"})
    except:
        return Response("Error loading game1.html", status=500)

# Serve `script.js`
@app.route('/script.js')
def serve_script(request):
    try:
        with open("script.js", "r") as file:
            return Response(file.read(), headers={"Content-Type": "application/javascript"})
    except:
        return Response("Error loading script.js", status=500)

# Serve `game1.js`
@app.route('/game1.js')
def serve_game1_js(request):
    try:
        with open("game1.js", "r") as file:
            return Response(file.read(), headers={"Content-Type": "application/javascript"})
    except:
        return Response("Error loading game1.js", status=500)

# Handle User Registration
@app.route('/register', methods=['POST'])
def register_user(request):
    try:
        data = request.json
        username = data.get("username", "").strip().upper()

        if not username:
            return Response(json.dumps({"error": "Invalid Username"}), status=400)

        userdata = load_json(USERDATA_FILE)
        if username not in userdata:
            userdata[username] = {"memory_mode": 0, "riddle_mode": 0}

        with open(USERDATA_FILE, "w") as file:
            json.dump(userdata, file)

        return Response(json.dumps({"message": "User Registered"}))
    except:
        return Response(json.dumps({"error": "Failed to process request"}), status=500)

# Fetch All Scores (Sorted)
@app.route('/get_all_scores')
def get_all_scores(request):
    userdata = load_json(USERDATA_FILE)
    scores_list = [{"username": user, "score": data["memory_mode"]} for user, data in userdata.items()]
    scores_list.sort(key=lambda x: x["score"])  # Sort by score (ascending)
    return Response(json.dumps(scores_list))

# Provide Riddle Data
@app.route('/get_riddle')
def serve_riddle(request):
    level = int(request.args.get("level", 1))
    return Response(json.dumps(get_riddle(level)))

# Handle Morse Code Input
@app.route('/check_morse', methods=['POST'])
def process_morse(request):
    try:
        data = request.json
        user_morse = data.get("morse", "").strip()
        return Response(json.dumps(check_morse_code(user_morse)))
    except:
        return Response(json.dumps({"message": "Error processing request", "success": False}))

# Start Server
def start_server():
    print("Starting Web Server on ESP32...")
    app.run(port=80)

# Run Everything
connect_wifi()
start_server()
