
# ────────────────────────────────────────────────────────────────────────────────
# USER‑TWEAKABLE CONSTANTS  🔧
# ────────────────────────────────────────────────────────────────────────────────

# Button‑to‑function mapping by matrix **row, col** indices
SLEEP_BTN = (0, 0)   # upper‑left key → toggles sleep / wake
ADD1_BTN   = (0, 1)   # +1 point  (yellow flash)
ADD2_BTN   = (0, 2)   # +2 points (purple flash 60 s)
SUB3_BTN   = (1, 0)   # –3 points (blue flash)
SUB5_BTN   = (1, 1)   # –5 points (blue flash)
SUB10_BTN  = (1, 2)   # –10 points (blue flash)

FLASH_TIME_SHORT = 0.5    # seconds for quick flashes
FLASH_TIME_LONG  = 60      # seconds for purple flash

IDLE_GREEN = (0, 8, 0)     # dim green under‑glow (GRB)

# ────────────────────────────────────────────────────────────────────────────────
import board, busio, digitalio, time, os
import displayio
from supervisors import ticks_ms, ticks_diff

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners import DiodeOrientation
from kmk.keys import KC   # placeholder keycodes in keymap

from adafruit_pixelbuf import PixelBuf
from neopixel_write import neopixel_write

# ───────────────────── Display setup ─────────────────────

displayio.release_displays()
i2c = busio.I2C(scl=board.GP7, sda=board.GP6)
import adafruit_displayio_ssd1306
DISPLAY_BUS = displayio.I2CDisplay(i2c, device_address=0x3C)
OLED_W, OLED_H = 128, 32
display = adafruit_displayio_ssd1306.SSD1306(DISPLAY_BUS, width=OLED_W, height=OLED_H)

group = displayio.Group()
display.show(group)

from adafruit_display_text import label
import terminalio
from adafruit_display_shapes.rect import Rect

text = label.Label(terminalio.FONT, text="", scale=2, x=0, y=12)
group.append(text)
bar_outline = Rect(0, OLED_H-10, OLED_W, 8, outline=1)
bar_fill    = Rect(1, OLED_H-9, 0, 6, fill=1)

# ───────────────────── NeoPixel helper ───────────────────

NUM_LEDS = 3
NEO_PIN = board.GP5
pixbuf = bytearray(NUM_LEDS*3)

def set_all(r,g,b):
    for i in range(NUM_LEDS):
        pixbuf[i*3:i*3+3] = bytes((g, r, b))  # GRB order
    neopixel_write(NEO_PIN, pixbuf)

def set_idle_green():
    set_all(*IDLE_GREEN)

# ───────────────────── Encoder setup ─────────────────────

import rotaryio
enc = rotaryio.IncrementalEncoder(board.GP8, board.GP9, divisor=4)
enc_btn = digitalio.DigitalInOut(board.GP10)
enc_btn.direction = digitalio.Direction.INPUT
enc_btn.pull = digitalio.Pull.UP
enc_last = enc.position

# ───────────────────── KMK keyboard/matrix ───────────────

kb = KMKKeyboard()
kb.col_pins = (board.GP0, board.GP1)  # C0, C1
kb.row_pins = (board.GP2, board.GP3)  # R0, R1
kb.diode_orientation = DiodeOrientation.COL2ROW
kb.keymap = [  # dummy keycodes – events handled manually
    [KC.NO, KC.NO, KC.NO,
     KC.NO, KC.NO, KC.NO]
]

# ───────────────────── Timer state machine ───────────────

DURATIONS = [60, 300, 600, 900, 1200, 1800, 2400]  # 1‑40 m
idx = 0
state_timer = 0  # 0=idle, 1=set, 2=run
start_time = 0

# ───────────────────── Points persistence ────────────────

POINTS_FILE = "/points.txt"

def load_points():
    try:
        with open(POINTS_FILE, "r") as f:
            return int(f.read().strip())
    except OSError:
        return 0

def save_points(val):
    try:
        with open(POINTS_FILE, "w") as f:
            f.write(str(val))
    except OSError:
        pass

points = load_points()

# ───────────────────── Flash control ─────────────────────

flash_end = 0
flash_color = (0,0,0)

# ───────────────────── Sleep mode ────────────────────────

sleep = False

def enter_sleep():
    global sleep
    sleep = True
    display.sleep(True)
    display.auto_refresh = False
    set_all(0,0,0)


def exit_sleep():
    global sleep
    sleep = False
    display.sleep(False)
    display.auto_refresh = True
    set_idle_green()

# ───────────────────── Helper functions ──────────────────

from adafruit_display_text import wrap_text_to_lines

def show_text(msg):
    group[:] = [text]
    text.text = msg


def show_setup_screen(sec):
    group[:] = [text]
    text.text = f"Set {sec//60}m"


def show_timer_screen(total):
    group[:] = [bar_outline, bar_fill, text]
    text.text = f"{total//60}m"
    bar_fill.width = 0

# ───────────────────── Initial visuals ───────────────────

show_text(f"Points: {points}")
set_idle_green()

# ───────────────────── Main loop ─────────────────────────

while True:
    kb.go()  # scan matrix for events

    # === Handle matrix‑based key events ===
    evt = kb.keys.events.get() if kb.keys.events else None
    if evt and not sleep:
        row, col = divmod(evt.key_number, 3)
        if evt.pressed:  # only on press
            if (row, col) == SLEEP_BTN:
                enter_sleep()
            elif (row, col) == ADD1_BTN:
                points += 1
                save_points(points)
                show_text(f"Points: {points}")
                flash_color, flash_end = (255,255,0), time.monotonic()+FLASH_TIME_SHORT
            elif (row, col) == ADD2_BTN:
                points += 2
                save_points(points)
                show_text(f"Points: {points}")
                flash_color, flash_end = (128,0,128), time.monotonic()+FLASH_TIME_LONG
            elif (row, col) == SUB3_BTN:
                points -= 3
                save_points(points)
                show_text(f"Points: {points}")
                flash_color, flash_end = (0,0,255), time.monotonic()+FLASH_TIME_SHORT
            elif (row, col) == SUB5_BTN:
                points -= 5
                save_points(points)
                show_text(f"Points: {points}")
                flash_color, flash_end = (0,0,255), time.monotonic()+FLASH_TIME_SHORT
            elif (row, col) == SUB10_BTN:
                points -= 10
                save_points(points)
                show_text(f"Points: {points}")
                flash_color, flash_end = (0,0,255), time.monotonic()+FLASH_TIME_SHORT

    # === Sleep toggle button wake‑up ===
    if evt and sleep and evt.pressed:
        row,col = divmod(evt.key_number,3)
        if (row,col)==SLEEP_BTN:
            exit_sleep()
            show_text(f"Points: {points}")

    now = time.monotonic()

    # === Flash management ===
    if flash_end and now < flash_end:
        set_all(*flash_color)
    elif flash_end and now >= flash_end:
        flash_end = 0
        set_idle_green()

    # === Encoder button presses (timer state machine) ===
    if not sleep:
        if not enc_btn.value:  # pressed
            while not enc_btn.value:
                time.sleep(0.01)  # wait release (simple debounce)
            if state_timer == 0:
                state_timer = 1  # enter duration set
                idx = 0
                show_setup_screen(DURATIONS[idx])
            elif state_timer == 1:
                state_timer = 2  # start timer
                start_time = now
                show_timer_screen(DURATIONS[idx])
            elif state_timer == 2:
                # cancel
                state_timer = 0
                group[:] = [text]
                text.text = f"Points: {points}"

        # Encoder rotation
        if state_timer == 1:
            pos = enc.position
            delta = pos - enc_last
            if delta:
                idx = max(0, min(len(DURATIONS)-1, idx + (1 if delta>0 else -1)))
                show_setup_screen(DURATIONS[idx])
                enc_last = pos

        # Timer running
        if state_timer == 2:
            elapsed = now - start_time
            bar_fill.width = int((OLED_W-2)*min(1.0, elapsed/DURATIONS[idx]))
            if elapsed >= DURATIONS[idx]:
                flash_color, flash_end = (0,255,0), now+3  # green flash 3s
                state_timer = 0
                show_text(f"Points: {points}")

    time.sleep(0.01)
