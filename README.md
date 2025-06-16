# Time-Machine
Deceptively small macropad (could fit in your palm)

![image](https://github.com/user-attachments/assets/f33d87a3-e40c-47d5-a0a7-2164a2c59ac9)

Time Machine is a KMK-powered, 6-key + Rotary Encoder, OLED display, Macropad with underglow lighting. 


KMK firmware for the custom Hackpad
-----------------------------------
Features
~~~~~~~~
* 6 push‑buttons scanned by KMK (left as plain keycodes – customize later)
* EC11 rotary encoder (GP8=A, GP9=B, GP10=SW)
    * Short‑press once → enter **Timer‑Setup** mode
    * Turn knob → cycle through preset durations
      (1, 5, 10, 15, 20, 30, 40 minutes)
    * Short‑press again → start the countdown
* 0.91″ SSD1306 OLED (I²C on GP6=SDA, GP7=SCL)
    * Shows selected duration or live progress bar + remaining time
* 3× SK6812 LEDs daisy‑chained on GP5 (optional flash on timer end)

Requires:
* CircuitPython ≥ 9.0 or RP2040‑UF2 w/ displayio support
* `adafruit_displayio_ssd1306` and `adafruit_display_text` libraries in /lib
* KMK (copy kmk/ into CIRCUITPY drive)

Save this file as `code.py` or `main.py` on the XIAO‑RP2040.
