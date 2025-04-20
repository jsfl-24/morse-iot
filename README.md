#  MOCO – Morse Code Based IoT Game

**Moco** is an innovative Morse Code-based IoT game built using ESP32 and ESP8266 (NodeMCU). It merges embedded systems, real-time web technologies, and interactive gameplay to create a unique and educational experience.

---

##  Project Highlights

-  **Real-time Morse input** via push buttons connected to ESP8266
-  Multiple game modes (Memory Game, Riddle Game, CSE Quiz)
-  **WebSocket bridge** between ESP32 (main game logic) and ESP8266 (hardware interface)
-  Real-time LCD display updates and web dashboard using WebSockets
-  Player data and game questions stored in JSON
-  Feedback through buzzer and LEDs
-  Wi-Fi enabled communication

---

##  Hardware Components

| Component         | Description                            |
|------------------|----------------------------------------|
| ESP32            | Core game controller & server host     |
| ESP8266 (NodeMCU)| Handles GPIO input and LCD display     |
| Push Buttons (x5)| Dot, Dash, Space, Clear, Submit        |
| HD44780 LCD (16x2)| Connected to ESP8266 via GPIO          |
| Buzzer           | Audio feedback for Morse input         |
| LEDs (optional)  | Visual feedback (correct/incorrect)    |
| Resistors, Wires | Standard components for button inputs  |
| Power Source     | USB or 5V adapter                      |

---

##  Game Modes

1. **Memory Game** – Reproduce a sequence of Morse code patterns
2. **Morse Riddle Game** – Decode riddles using Morse code
3. **CSE Quiz Game** – Answer CSE-related questions with Morse code inputs

---

##  Communication Architecture

- **ESP8266 NodeMCU**:  
   - Reads button inputs with debounce  
   - Controls the LCD display  
   - Sends Morse code input to ESP32 via bridge (e.g., UART or WebSockets)

- **ESP32**:  
   - Hosts WebSocket & HTTP server  
   - Maintains game logic, user data, and web interface  
   - Receives Morse input from ESP8266  
   - Sends game state and feedback in real-time

- **Frontend (Web)**:  
   - Built with HTML, CSS, JavaScript  
   - Communicates with ESP32 via WebSocket and AJAX  
   - Displays player data, questions, and game progress

---

##  How to Setup
### Prerequisites

1. **Install esptool**  
   You need to have `esptool` installed to flash the firmware onto your ESP32 and ESP8266. You can install it using pip:

   ```bash
   pip install esptool

2. **Download the Firmware**

Download the MicroPython firmware for ESP32 from [MicroPython ESP32 Firmware.](https://micropython.org/download/esp32/)

Download the MicroPython firmware for ESP8266 from [MicroPython ESP8266 Firmware.](https://micropython.org/download/esp8266/)

### Flashing Firmware

#### 1. **Flash ESP32**

1. Put the ESP32 in **flash mode** by pressing and holding the **BOOT** button while connecting it to your computer.
2. Flash the firmware using the following command:

   ```bash
   esptool.py --chip esp32 --port <YOUR_PORT> write_flash -z 0x1000 <path_to_firmware.bin>
#### 2. **Flash ESP8266 (NodeMCU)**

1. Put the ESP8266 in **flash mode** by holding the **FLASH** button while connecting it to your computer.

2. Flash the firmware using the following command:

   ```bash
   esptool.py --chip esp8266 --port <YOUR_PORT> write_flash 0x00000 <path_to_firmware.bin>


---

### Recommended Software: Thonny IDE

---

For easy development and uploading scripts to both ESP32 and ESP8266, it's recommended to use **Thonny** IDE. Thonny is a beginner-friendly Python IDE that works well with MicroPython and supports both ESP32 and ESP8266 boards.

1. **Install Thonny**:  
   Download and install Thonny from the official website: [https://thonny.org/](https://thonny.org/).

2. **Configure Thonny for MicroPython**:
   - Open Thonny IDE.
   - Go to **Tools** > **Options**.
   - Under the **Interpreter** tab, select **MicroPython (ESP32/ESP8266)** from the dropdown list.
   - Choose the correct **Port** for your connected device.
   - Click **OK** to apply the changes.

3. **Uploading Scripts**:  
   Once Thonny is set up, you can upload your scripts to the ESP32/ESP8266 by selecting **File** > **Save As** and choosing the device as the save location.

---

##  How to Run

1. **Flash ESP32** with MicroPython and upload:
   - `main.py`
   - `userdata.json`
   - `cseq.json`
   - `riddles.json`
   - Any other game-related files cloned from the repository.

2. **Flash ESP8266** with GPIO input code:
   - All game-related files cloned from the repository.
   - Button press logic
   - LCD driver logic (HD44780 via GPIO)
   - Communication bridge logic (e.g., UART/WebSocket to ESP32)

3. Connect both devices to the **same Wi-Fi** network.

4. Access the game interface via the **ESP32 IP Address** in browser.

---


##  Folder Structure

```text
/moco
├── esp32/
│ ├── boot.py
│ ├── main.py
│ ├── cseq.json
│ ├── current_user.txt
│ ├── game.js
│ ├── game1.html
│ ├── game1.js
│ ├── game2.html
│ ├── game2.js
│ ├── game3.html
│ ├── game3.js
│ ├── gpio.py
│ ├── i2c_lcd.py
│ ├── index.html
│ ├── lcd_api.py
│ ├── microdot.mpy
│ ├── morse_input.txt
│ ├── pymakr.conf
│ ├── result.html
│ ├── riddles.json
│ ├── script.js
│ ├── userdata.json
│ └── wifi.py

├── esp82/
│ ├── boot.py
│ ├── esp32_gpio_lcd.py
│ ├── lcd_api.py
│ ├── main.py
│ └── morse_input.txt
```

---

---

## Developed By

**Jasfal (jsfl-24)**  
B.Tech CSE | Embedded Systems & IoT Enthusiast  
GitHub: [github.com/jsfl-24](https://github.com/jsfl-24)
