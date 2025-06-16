# Time-Machine
Deceptively small macropad (could fit in your palm)

![image](https://github.com/user-attachments/assets/f33d87a3-e40c-47d5-a0a7-2164a2c59ac9)

Time Machine is a KMK-powered, 6-key + Rotary Encoder, OLED display, Macropad with underglow lighting. 


KMK firmware for the custom Hackpad
-----------------------------------
Features
~~~~~~~~
* Constants at the top define which matrix key does what—easy to tweak later.
* A sleep toggle (OLED off, inputs ignored until woken).
* EC11 rotary encoder (GP8=A, GP9=B, GP10=SW)
    * Short‑press once → enter **Timer‑Setup** mode
    * Turn knob → cycle through preset durations
      (1, 5, 10, 15, 20, 30, 40 minutes)
    * Short‑press again → start the countdown
* 0.91″ SSD1306 OLED (I²C on GP6=SDA, GP7=SCL)
    * Shows selected duration or live progress bar + remaining time
* 3× SK6812 LEDs daisy‑chained on GP5 (optional flash on timer end)
* Stores a persistent points counter in /points.txt and flashes the LEDs:
    * +1 → yellow flash
    * +2 → purple for 1 minute
    * negative actions → blue flash
 * Two under‑glow LEDs stay dim green whenever no other colour is flashing.
~~~~~~~~~~

Requires:
* CircuitPython ≥ 9.0 or RP2040‑UF2 w/ displayio support
* `adafruit_displayio_ssd1306` and `adafruit_display_text` libraries in /lib
* KMK (copy kmk/ into CIRCUITPY drive)

Save this file as `code.py` or `main.py` on the XIAO‑RP2040.



# Design
This was my first time doing a hardware project! Thanks to all the friends that I bugged constantly :P

## PCB
I learned how to use a matrix to get all my features onto the XIAO microcontroller perfectly
![image](https://github.com/user-attachments/assets/d8574200-8297-4ece-b1d0-8506bd8c1c5f)
![image](https://github.com/user-attachments/assets/4e7ec694-4a71-4d11-887b-7e6afa26e2ec)
The schematic and the PCB were made in KiCad

## Case
First time CADing too! It ain't much, but it's honest work.
![image](https://github.com/user-attachments/assets/cc13083d-e474-4958-8925-a6cd7e525abf)
Case was made using Autodesk Fusion

## Firmware
Time Machine was made with custom-coded firmware written with the KMK library in Python

# BOM
*6 cans of redbull not included

## Electronics
* 1x XIAO RP2040
* 1x EC11E Rotary Encoder (with switch)
* 1x Rotary Encoder Knob
* 1x 0.91" OLED Display
* 6x Cherry MX Switches
* 6x Blank DSA Keycaps
* 6x Diode (THT)
* 3x SK6812 Mini LEDs
* 1x 330 Ohm Resistor

## Case
* 1x case_top.stl
* 1x case_plt.stl
* 1x case_btm.stl
* 3x M3x16 screw
* 4x 10mm Rubber Feet

