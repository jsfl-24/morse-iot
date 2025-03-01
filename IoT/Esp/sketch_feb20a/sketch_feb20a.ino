#include <SPI.h>
#include <SD.h>

#define SD_CS_PIN 5 // Chip Select pin for SD card module

void setup() {
  // Initialize Serial Monitor at 115200 baud rate
  Serial.begin(115200);
  delay(1000); // Wait for serial to initialize

  // Initialize SPI for SD card
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("SD card initialization failed!");
    return;
  }

  Serial.println("SD card initialized successfully!");

  // Try creating or opening a test file and writing data
  File testFile = SD.open("/test.txt", FILE_WRITE);
  if (testFile) {
    testFile.println("Hello from ESP32!");
    testFile.close();
    Serial.println("Data written to test.txt successfully.");
  } else {
    Serial.println("Error opening test.txt for writing.");
  }

  // Try opening the file to read the data
  testFile = SD.open("/test.txt");
  if (testFile) {
    Serial.println("Reading from test.txt:");
    while (testFile.available()) {
      Serial.write(testFile.read());  // Read and print data
    }
    testFile.close();
    Serial.println("\nReading complete.");
  } else {
    Serial.println("Error opening test.txt for reading.");
  }
}

void loop() {
  // Nothing to do in loop
}
