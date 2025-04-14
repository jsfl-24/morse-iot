import machine
import utime
from machine import Pin
from esp32_gpio_lcd import GpioLcd

# --- GPIO Pin Definitions ---
BUTTONS = {
    "dot": machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP),
    "dash": machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP),
    "space": machine.Pin(27, machine.Pin.IN, machine.Pin.PULL_UP),
    "clear": machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_UP),
    "submit": machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_UP),
}

BUZZER = machine.Pin(23, machine.Pin.OUT)

# LCD Setup (I2C-based)
lcd = GpioLcd(rs_pin=Pin(4),
              enable_pin=Pin(17),
              d4_pin=Pin(5),
              d5_pin=Pin(18),
              d6_pin=Pin(21),
              d7_pin=Pin(22),
              num_lines=2, num_columns=16)

morse_input = ""
CORRECT_ANSWER = "... --- ..."  # Example Morse code (SOS)

# --- Functions ---

def save_morse_input(data):
    """Save Morse input to a file."""
    with open("morse_input.txt", "w") as file:
        file.write(data)

def beep(duration):
    """Activate buzzer for given duration (ms)."""
    BUZZER.value(1)
    utime.sleep_ms(duration)
    BUZZER.value(0)

def update_lcd():
    """Display the current Morse input on LCD."""
    lcd.clear()
    lcd.putstr(morse_input[:16])  # Display first 16 characters

def check_button_hold(pin, symbol):
    """Handle button press with debounce and hold detection."""
    global morse_input
    start_time = utime.ticks_ms()
    
    while pin.value() == 0:  # While button is pressed
        utime.sleep_ms(10)
        if utime.ticks_diff(utime.ticks_ms(), start_time) >= 500:  # 500ms hold
            morse_input += symbol
            save_morse_input(morse_input)
            update_lcd()  # Update LCD display
            beep(150)  # Short beep for input feedback
            print(f"Registered input: {symbol}")
            return

# --- Main Loop ---
print("ESP32 Morse Input Ready...")

while True:
    if BUTTONS["dot"].value() == 0:
        check_button_hold(BUTTONS["dot"], ".")
    elif BUTTONS["dash"].value() == 0:
        check_button_hold(BUTTONS["dash"], "_")
    elif BUTTONS["space"].value() == 0:
        check_button_hold(BUTTONS["space"], "/")
    elif BUTTONS["clear"].value() == 0:
        morse_input = ""
        save_morse_input(morse_input)
        update_lcd()
        print("Morse input cleared!")
    elif BUTTONS["submit"].value() == 0:
        print(f"Submitted Morse Code: {morse_input}")
        if morse_input.strip() == CORRECT_ANSWER:
            print("✅ Correct!")
        else:
            print("❌ Incorrect!")
        beep(1000)  # Long beep for submission feedback
        morse_input = ""  # Reset after submission
        save_morse_input(morse_input)
        update_lcd()
    
    utime.sleep_ms(50)  # Small delay for stability
