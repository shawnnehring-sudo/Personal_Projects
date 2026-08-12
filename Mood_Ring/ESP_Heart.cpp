#include <WiFi.h>
#include <HTTPClient.h>

// --- WiFi credentials ---
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

// --- Flask server address (your computer's or Pi's local IP) ---
const char* serverUrl = "http://192.168.1.XX:5000/sensor_data";

const int PULSE_PIN = 34;  // ESP32 ADC-capable pin

void setup() {
  Serial.begin(115200);
  pinMode(PULSE_PIN, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP: " + WiFi.localIP().toString());
}

void loop() {
  int rawValue = analogRead(PULSE_PIN);  // 0-4095 on ESP32 (12-bit ADC)

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"raw_value\": " + String(rawValue) + "}";
    int responseCode = http.POST(payload);

    if (responseCode <= 0) {
      Serial.println("POST failed, error: " + http.errorToString(responseCode));
    }
    http.end();
  } else {
    Serial.println("WiFi disconnected!");
  }

  delay(100);  // ~10 samples/sec -- fast enough to detect heartbeat peaks
}