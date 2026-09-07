# RJ361 LED Piano Tutor

A software-first prototype for adding a 61-key LED learning guide to a
RockJam RJ361 keyboard.

## Current prototype

- 61-key virtual piano covering C2-C7 (MIDI 36-96)
- Clickable simulated key input
- Guided mode: the song waits until all required notes are pressed
- Timed mode: notes advance according to song timing
- Three-stage LED preview:
  - Green = current notes
  - Yellow = next notes
  - Blue = notes after next
  - Red = incorrect simulated key
- JSON song loading with no external Python dependencies
- MIDI file loading through `mido`
- Optional Wi-Fi/UDP control of an ESP32
- ESP32 firmware for 61 WS2812B/SK6812-style addressable LEDs

## Why Python on the laptop + C++ on the ESP32?

Python is used for the host application because GUI drawing, file parsing,
sequencing, and MIDI processing are far below the performance limits of a
modern laptop. It also makes iteration much faster.

C++ is used where timing and hardware access actually matter: the ESP32.

## Run the simulator

From the project directory:

Windows:

    py app/main.py

or:

    python app/main.py

The included JSON demo loads automatically and needs no packages.

Click the green piano key(s). In Guided mode, once every green note in the
current event is clicked, the next event becomes active.

Switch to Timed mode and press Start to make the song advance automatically.

## Enable MIDI import

Install:

    py -m pip install -r requirements.txt

Then click `Load Song` and select a `.mid` or `.midi` file.

The current MIDI loader:
- reads note-on events,
- accounts for MIDI tempo changes through Mido,
- groups nearly simultaneous note starts into chords,
- rejects notes outside the RJ361's C2-C7 range.

For the Wednesday MVP, MIDI is intentionally the first sheet-music
interchange format. MusicXML can be added next.

## ESP32 hardware

Suggested:
- ESP32
- WS2812B/SK6812 addressable LEDs
- external regulated 5 V LED supply
- common ground between ESP32 and LED supply
- 330-470 ohm series resistor on LED data
- logic-level shifter recommended for a reliable 3.3 V ESP32 -> 5 V LED signal
- bulk capacitor across LED 5 V / GND near the LED rail

Do NOT power 61 LEDs directly from the ESP32 regulator.

### Firmware

Open:

    firmware/esp32_led_controller/esp32_led_controller.ino

Install FastLED in Arduino IDE.

Set:
- `WIFI_SSID`
- `WIFI_PASSWORD`
- `DATA_PIN`

Upload to the ESP32 and open Serial Monitor at 115200 baud. It prints the
ESP32's IP address.

Type that IP into the laptop application's `ESP32 IP` box and click Apply.

Both devices must be on the same network.

## Network protocol

The laptop sends a complete RGB framebuffer over UDP port 4210:

    byte 0 = 0xA5
    next 183 bytes = RGB values for 61 LEDs

This keeps the firmware independent of song parsing and UI logic.

## RJ361 key detection

The RJ361 documentation describes its USB connector as an MP3-playback USB
input, not a USB-MIDI connection. Therefore this project does not assume that
the keyboard can report key events externally.

The software intentionally routes all input through one logical function:

    note_pressed(midi_note)

Today, the virtual piano calls it. A future hardware input adapter can call the
same function without changing the playback engine.

The best hardware investigation path is likely the keyboard's internal key
scan circuitry, but that should only be attempted after identifying the
RJ361 PCB/matrix with a multimeter or logic analyzer. Do not connect ESP32
GPIO directly to unknown keyboard matrix lines until their voltage and scan
behavior are known.

## Next milestones

1. MusicXML import.
2. Configurable tempo scaling.
3. MIDI/USB input adapter for keyboards that provide MIDI.
4. Inspect RJ361 internal key matrix and create an electrically isolated
   key-event interface.
5. Calibrate physical LED locations to actual white/black key centers.
6. Add practice statistics such as wrong notes and completion time.
