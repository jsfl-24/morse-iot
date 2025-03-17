import network
import time

SSID = "Asianet"  # Replace with your WiFi SSID
PASSWORD = "04042012"  # Replace with your WiFi Password

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        
        timeout = 10  # 10-second timeout
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
    
    if wlan.isconnected():
        print("Connected! IP Address:", wlan.ifconfig()[0])
    else:
        print("Failed to connect to Wi-Fi")
    
    return wlan.ifconfig()[0] if wlan.isconnected() else None

