#include <WiFi.h>
#include <WiFiUdp.h>
#include <FastLED.h>

// ---------- EDIT THESE ----------
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

constexpr uint8_t DATA_PIN = 5;
constexpr uint16_t UDP_PORT = 4210;
constexpr int LED_COUNT = 61;
constexpr uint8_t BRIGHTNESS = 80;
// -------------------------------

constexpr uint8_t MAGIC = 0xA5;
constexpr int PACKET_SIZE = 1 + LED_COUNT * 3;

CRGB leds[LED_COUNT];
WiFiUDP udp;
uint8_t packet[PACKET_SIZE];

void clearLEDs() {
  fill_solid(leds, LED_COUNT, CRGB::Black);
  FastLED.show();
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("Connected. ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);

  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, LED_COUNT);
  FastLED.setBrightness(BRIGHTNESS);
  clearLEDs();

  connectWiFi();
  udp.begin(UDP_PORT);

  Serial.print("Listening for 61-key LED frames on UDP port ");
  Serial.println(UDP_PORT);
}

void loop() {
  int incomingSize = udp.parsePacket();
  if (incomingSize <= 0) {
    delay(1);
    return;
  }

  if (incomingSize != PACKET_SIZE) {
    // Drain any unexpected packet.
    while (udp.available()) {
      udp.read();
    }
    return;
  }

  int bytesRead = udp.read(packet, PACKET_SIZE);
  if (bytesRead != PACKET_SIZE || packet[0] != MAGIC) {
    return;
  }

  int p = 1;
  for (int i = 0; i < LED_COUNT; i++) {
    uint8_t r = packet[p++];
    uint8_t g = packet[p++];
    uint8_t b = packet[p++];
    leds[i] = CRGB(r, g, b);
  }

  FastLED.show();
}
