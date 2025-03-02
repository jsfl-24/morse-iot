#include <WiFi.h>
#include <WebServer.h>
#include <SD.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "Assi";
const char* password = "04042012";

// GPIO pins
#define DOT_BUTTON 4
#define DASH_BUTTON 5
#define RESET_BUTTON 18
#define ENTER_BUTTON 19
#define BUZZER_PIN 21

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2); // I2C address 0x27, 16x2 display

// Game variables
String morseInput = "";
int currentLevel = 1;
String currentRiddle = "";
String currentAnswer = "";

// Web server
WebServer server(80);

// LEDC (PWM) settings for buzzer
#define LEDC_CHANNEL 0 // Use channel 0 for the buzzer
#define LEDC_RESOLUTION 8 // 8-bit resolution (0-255)
#define LEDC_BASE_FREQ 5000 // Base frequency for PWM

// Morse code lookup table
const String morseCode[] = {
  ".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."
};

// Convert alphabetic answer to Morse code
String convertToMorse(String text) {
  String morse = "";
  for (char c : text) {
    if (c >= 'A' && c <= 'Z') {
      morse += morseCode[c - 'A'] + " ";
    } else if (c >= 'a' && c <= 'z') {
      morse += morseCode[c - 'a'] + " ";
    }
  }
  morse.trim(); // Remove trailing space
  return morse;
}

// Load riddles from SD card
void loadRiddle() {
  File file = SD.open("/data/riddles.json");
  if (file) {
    StaticJsonDocument<1024> doc;
    deserializeJson(doc, file);
    String levelKey = "level" + String(currentLevel);
    JsonArray levelRiddles = doc[levelKey];
    int randomIndex = random(0, levelRiddles.size());
    currentRiddle = levelRiddles[randomIndex]["riddle"].as<String>();
    currentAnswer = convertToMorse(levelRiddles[randomIndex]["answer"].as<String>());
    file.close();
  }
  lcd.clear();
  lcd.print("Level " + String(currentLevel));
  lcd.setCursor(0, 1);
  lcd.print(currentRiddle);
}

// Generate a tone using LEDC
void playTone(int frequency, int duration) {
  ledcWriteTone(LEDC_CHANNEL, frequency); // Set frequency
  delay(duration); // Play for the specified duration
  ledcWriteTone(LEDC_CHANNEL, 0); // Stop the tone
}

// Handle Morse code input
void handleInput(char symbol) {
  morseInput += symbol;
  lcd.setCursor(0, 1);
  lcd.print(morseInput);
  if (symbol == '.') playTone(1000, 100); // Short beep for dot
  else playTone(1000, 300); // Long beep for dash
}

// Reset Morse input
void resetInput() {
  morseInput = "";
  lcd.setCursor(0, 1);
  lcd.print("                "); // Clear input line
}

// Validate Morse input
void validateInput() {
  if (morseInput == currentAnswer) {
    playTone(1000, 500); // Success beep
    currentLevel++;
    loadRiddle();
  } else {
    playTone(1000, 100); // Double beep for error
    delay(100);
    playTone(1000, 100);
  }
  resetInput();
}

// Handle root URL
void handleRoot() {
  String html = "<html><body><h1>IoT Morse Code Game</h1><p>Welcome to the game!</p></body></html>";
  server.send(200, "text/html", html);
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Initialize buttons
  pinMode(DOT_BUTTON, INPUT);
  pinMode(DASH_BUTTON, INPUT);
  pinMode(RESET_BUTTON, INPUT);
  pinMode(ENTER_BUTTON, INPUT);

  // Initialize LCD
  lcd.begin(16, 2); // 16 columns, 2 rows
  lcd.backlight();
  lcd.print("IoT Morse Game");

  // Initialize SD card
  if (!SD.begin(15)) { // CS pin for SD card is GPIO 15
    lcd.print("SD Card Failed");
    return;
  }

  // Configure LEDC for buzzer
  ledcSetup(LEDC_CHANNEL, LEDC_BASE_FREQ, LEDC_RESOLUTION); // Set up LEDC channel
  ledcAttachPin(BUZZER_PIN, LEDC_CHANNEL); // Attach buzzer pin to LEDC channel

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    lcd.print(".");
  }
  lcd.clear();
  lcd.print("WiFi Connected");
  lcd.setCursor(0, 1);
  lcd.print(WiFi.localIP());

  // Load first riddle
  loadRiddle();

  // Start web server
  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  // Handle button inputs
  if (digitalRead(DOT_BUTTON) == HIGH) {
    handleInput('.');
    delay(200); // Debounce delay
  }
  if (digitalRead(DASH_BUTTON) == HIGH) {
    handleInput('-');
    delay(200); // Debounce delay
  }
  if (digitalRead(RESET_BUTTON) == HIGH) {
    resetInput();
    delay(200); // Debounce delay
  }
  if (digitalRead(ENTER_BUTTON) == HIGH) {
    validateInput();
    delay(200); // Debounce delay
  }

  // Handle web server requests
  server.handleClient();
}