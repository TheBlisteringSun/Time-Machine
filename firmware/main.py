import time
import board
import busio
import digitalio
import displayio
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from neopixel_write import neopixel_write
from supervisors import ticks_ms

# ────────────────────────────────────────────────────────────────────────────────
# ‑‑‑ Display setup ‑‑‑
# ────────────────────────────────────────────────────────────────────────────────
displayio.release_displays()
i2c = busio.I2C(scl=board.GP7, sda=board.GP6)

OLED_WIDTH = 128
OLED_HEIGHT = 32

import adafruit_displayio_ssd1306

DISPLAY_BUS = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(DISPLAY_BUS, width=OLED_WIDTH, height=OLED_HEIGHT)

main_group = displayio.Group()
display.show(main_group)

def clear_display():
    main_group.pop()
    main_group.append(displayio.Bitmap(1, 1, 1))  # placeholder

# ────────────────────────────────────────────────────────────────────────────────
# ‑‑‑ Graphics helpers ‑‑‑
# ────────────────────────────────────────────────────────────────────────────────
from adafruit_display_text import label
import terminalio
from adafruit_display_shapes.rect import Rect

bar_height = 8
bar_y = OLED_HEIGHT - bar_height - 2
bar_outline = Rect(0, bar_y, OLED_WIDTH, bar_height, outline=1, fill=None)
bar_fill = Rect(1, bar_y + 1, 0, bar_height - 2, fill=1)

text_label = label.Label(terminalio.FONT, text="", scale=2, x=0, y=12)

def update_duration_text(seconds):
    minutes = seconds // 60
    text_label.text = f"{minutes}m"

def update_progress(elapsed, total):
    pct = min(1.0, elapsed / total)
    bar_fill.width = int((OLED_WIDTH - 2) * pct)

def show_setup_screen(seconds):
    main_group[:] = []  # clear
    update_duration_text(seconds)
    main_group.append(text_label)


def show_timer_screen(total_seconds):
    main_group[:] = []
    main_group.append(bar_outline)
    main_group.append(bar_fill)
    update_progress(0, total_seconds)
    update_duration_text(total_seconds)
    main_group.append(text_label)

# ────────────────────────────────────────────────────────────────────────────────
# ‑‑‑ Rotary encoder setup ‑‑‑
# ────────────────────────────────────────────────────────────────────────────────
import rotaryio
enc = rotaryio.IncrementalEncoder(board.GP8, board.GP9, divisor=4)
enc_button = digitalio.DigitalInOut(board.GP10)
enc_button.direction = digitalio.Direction.INPUT
enc_button.pull = digitalio.Pull.UP

last_enc_pos = enc.position

# ────────────────────────────────────────────────────────────────────────────────
# ‑‑‑ KMK keyboard base (for the six keys) ‑‑‑
# ────────────────────────────────────────────────────────────────────────────────
keyboard = KMKKeyboard()
keyboard.keymap = [
    [KC.A, KC.B, KC.C, KC.D, KC.E, KC.F]  # placeholder keycodes
]

# ────────────────────────────────────────────────────────────────────────────────
# ‑‑‑ Timer state machine ‑‑‑
# ────────────────────────────────────────────────────────────────────────────────
DURATIONS = [60, 300, 600, 900, 1200, 1800, 2400]  # sec
selection_idx = 0

STATE_IDLE = 0
STATE_SET = 1
STATE_RUN = 2
state = STATE_IDLE

start_time = 0
current_duration = DURATIONS[selection_idx]

# debouncing helper
button_debounced = enc_button.value

# LED helper (single data pin / daisy‑chain)
NEO_PIN = board.GP5
NUM_LEDS = 3

pixel = bytearray(NUM_LEDS * 3)


def neopixel_fill(r, g, b):
    for i in range(NUM_LEDS):
        pixel[i * 3 : i * 3 + 3] = bytes((g, r, b))  # GRB order
    neopixel_write(NEO_PIN, pixel)


# ────────────────────────────────────────────────────────────────────────────────
# ‑‑‑ Main loop ‑‑‑
# ────────────────────────────────────────────────────────────────────────────────
show_setup_screen(current_duration)

while True:
    keyboard.go()

    # === BUTTON PRESS (state transitions) ===
    now_button = enc_button.value
    if button_debounced and not now_button:
        # falling edge – pressed
        if state == STATE_IDLE:
            state = STATE_SET
            selection_idx = 0
            current_duration = DURATIONS[selection_idx]
            show_setup_screen(current_duration)
        elif state == STATE_SET:
            state = STATE_RUN
            start_time = time.monotonic()
            show_timer_screen(current_duration)
        elif state == STATE_RUN:
            # press during running -> cancel & reset
            state = STATE_IDLE
            main_group[:] = []
            neopixel_fill(0, 0, 0)
        # NOTE: add small vibrate / beep here if desired
    button_debounced = now_button

    # === ROTATION ===
    if state == STATE_SET:
        pos = enc.position
        delta = pos - last_enc_pos
        if delta != 0:
            selection_idx = max(0, min(len(DURATIONS) - 1, selection_idx + (1 if delta > 0 else -1)))
            current_duration = DURATIONS[selection_idx]
            show_setup_screen(current_duration)
        last_enc_pos = pos

    # === TIMER RUN ===
    if state == STATE_RUN:
        elapsed = time.monotonic() - start_time
        update_progress(elapsed, current_duration)
        if elapsed >= current_duration:
            neopixel_fill(255, 0, 0)  # flash red on completion
            state = STATE_IDLE
            time.sleep(1)
            neopixel_fill(0, 0, 0)
            main_group[:] = []

    # small sleep to give USB & other tasks time
    time.sleep(0.01)
