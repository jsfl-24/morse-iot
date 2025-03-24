import uasyncio as asyncio
import machine
import urequests

# Define GPIO pins for the five push buttons
DOT_PIN = 14       # Button for "."
DASH_PIN = 27      # Button for "_"
SPACE_PIN = 26     # Button for "/"
CLEAR_PIN = 25     # Button for "clear"
SUBMIT_PIN = 33    # Button for "submit"

# Set up buttons as input with pull-up resistors (active-low)
dot_button = machine.Pin(DOT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
dash_button = machine.Pin(DASH_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
space_button = machine.Pin(SPACE_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
clear_button = machine.Pin(CLEAR_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
submit_button = machine.Pin(SUBMIT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

# ESP32 server IP (adjust if needed)
SERVER_URL = "http://192.168.1.2/api/morse-input"

async def send_morse(symbol):
    """Send Morse input to the Microdot server."""
    try:
        response = urequests.post(SERVER_URL, json={"input": symbol})
        response.close()
    except Exception as e:
        print("Error sending Morse input:", e)

async def button_listener():
    """Continuously check button presses and send Morse input."""
    while True:
        if not dot_button.value():   # "." pressed
            await send_morse(".")
            await asyncio.sleep(0.3)  # Debounce delay

        if not dash_button.value():  # "_" pressed
            await send_morse("_")
            await asyncio.sleep(0.3)

        if not space_button.value():  # "/" pressed
            await send_morse("/")
            await asyncio.sleep(0.3)

        if not clear_button.value():  # Clear input
            await send_morse("clear")
            await asyncio.sleep(0.3)

        if not submit_button.value():  # Submit Morse input
            await send_morse("submit")
            await asyncio.sleep(0.3)

        await asyncio.sleep(0.05)  # Short delay to reduce CPU usage

# Run the button listener loop
async def main():
    await button_listener()

# Start asyncio event loop
asyncio.run(main())
