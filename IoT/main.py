import network
import socket
import ujson as json
import os

# WiFi Configuration
SSID = "Asianet"
PASSWORD = "04042012"

# JSON File
USERDATA_FILE = "userdatas.json"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print("Connected! IP:", wlan.ifconfig()[0])

def load_file(filename):
    """Reads a file from ESP32 storage."""
    try:
        with open(filename, "r") as file:
            return file.read()
    except:
        return "File Not Found"

def read_userdata():
    """Loads user data from JSON file or returns an empty dictionary."""
    if USERDATA_FILE in os.listdir():
        try:
            with open(USERDATA_FILE, "r") as file:
                return json.load(file)
        except:
            return {}  # Return empty dict if file is corrupted
    return {}

def save_userdata(userdata):
    """Saves user data to JSON file."""
    with open(USERDATA_FILE, "w") as file:
        json.dump(userdata, file)

def register_user(request):
    """Handles user registration and stores username in JSON file."""
    try:
        content = request.split("\r\n\r\n")[-1]  # Extract JSON payload
        user_data = json.loads(content)
        username = user_data.get("username", "").strip().upper()

        if not username:
            return "HTTP/1.1 400 Bad Request\n\n{\"error\": \"Invalid Username\"}"

        userdata = read_userdata()
        if username not in userdata:
            userdata[username] = {"memory_mode": 0, "riddle_mode": 0}  # Initialize scores

        save_userdata(userdata)
        return "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"message\": \"User Registered\"}"
    except:
        return "HTTP/1.1 500 Internal Server Error\n\n{\"error\": \"Failed to process request\"}"

def serve_file(request):
    """Serves requested files or handles API endpoints."""
    if "GET /script.js" in request:
        return "HTTP/1.1 200 OK\nContent-Type: application/javascript\n\n" + load_file("script.js")
    elif "POST /register" in request:
        return register_user(request)
    else:  # Default to index.html
        return "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + load_file("index.html")

def start_web_server():
    """Starts a simple web server on ESP32."""
    addr = ("", 80)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(addr)
    s.listen(5)
    print("Web server started on port 80")

    while True:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        response = serve_file(request)
        conn.send(response)
        conn.close()

# Run everything
connect_wifi()
start_web_server()
