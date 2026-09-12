"""
Velocidev - main sailing firmware v2

Two display modes on the 7-segment, switched by the OLED FeatherWing's buttons:
- SPEED: current GPS speed over ground, right-justified as X.X kt, top-right dot lit
- TIMER: 5-minute countdown as MM:SS, colon lit. When the countdown hits 00:00,
        the display auto-switches back to SPEED (once per run, so a manual visit
        to the timer view after expiry still shows 00:00).

Buttons (OLED FeatherWing, active-low with on-board pull-ups):
- A (D9): if the timer isn't running (never started or wound down), start it. Always switch to the timer view.
- B (D6): show the timer on the 7-segment
- C (D5): show the GPS speed on the 7-segment

Hardware:
- Adafruit Feather RP2040 Adalogger
- Adafruit Ultimate GPS FeatherWing (stacked)
- Adafruit 1.2" 4-digit 7-segment LED (HT16K33) via STEMMA QT
- Adafruit 128x64 OLED FeatherWing (stacked, buttons used; display not driven)
"""

import time
import board
import busio
import digitalio
import displayio
import adafruit_gps
from adafruit_ht16k33.segments import BigSeg7x4

# Release any leftover display state from prior test scripts (defensive; OLED is not driven here)
displayio.release_displays()

# --- Hardware setup ---
i2c = board.I2C()
display = BigSeg7x4(i2c)
display.brightness = 1.0

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0.1)
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

def _make_button(pin):
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    return b

btn_a = _make_button(board.D9)  # start 5-min timer
btn_b = _make_button(board.D6)  # switch to timer view
btn_c = _make_button(board.D5)  # switch to speed view

# --- Boot self-test ---
display.fill(1)
time.sleep(1.0)
display.fill(0)
display.print("----")

# --- State ---
UPDATE_INTERVAL = 0.5
TIMER_DURATION = 300  # 5 minutes in seconds

MODE_SPEED = "speed"
MODE_TIMER = "timer"
current_mode = MODE_SPEED
last_rendered_mode = None

timer_start = None  # monotonic timestamp when A was last pressed; None = never started
timer_expired_handled = False  # True after we've auto-switched to speed for the current run

speed_samples = [0.0, 0.0, 0.0]

# Button edge-detection state (True = pressed, since buttons are active-low)
btn_a_last = False
btn_b_last = False
btn_c_last = False

last_update = time.monotonic()

while True:
    gps.update()

    # --- Buttons: poll every iteration, fire on the press edge ---
    a_pressed = not btn_a.value
    b_pressed = not btn_b.value
    c_pressed = not btn_c.value

    if a_pressed and not btn_a_last:
        # Start the timer only if it's never been started or has already wound down;
        # a press while it's still running just switches the view.
        t = time.monotonic()
        if timer_start is None or (t - timer_start) >= TIMER_DURATION:
            timer_start = t
            timer_expired_handled = False
        current_mode = MODE_TIMER
    if b_pressed and not btn_b_last:
        current_mode = MODE_TIMER
    if c_pressed and not btn_c_last:
        current_mode = MODE_SPEED

    btn_a_last = a_pressed
    btn_b_last = b_pressed
    btn_c_last = c_pressed

    # --- Display: refresh on the normal cadence, or immediately on a mode switch ---
    now = time.monotonic()
    mode_changed = current_mode != last_rendered_mode
    if mode_changed or now - last_update >= UPDATE_INTERVAL:
        last_update = now
        led.value = not led.value

        if mode_changed:
            # Wipe segments and both decorations so nothing lingers between modes
            display.fill(0)
            display.colon = False
            display.ampm = False
            last_rendered_mode = current_mode

        if current_mode == MODE_SPEED:
            if gps.has_fix and gps.speed_knots is not None:
                speed_samples[0] = speed_samples[1]
                speed_samples[1] = speed_samples[2]
                speed_samples[2] = gps.speed_knots
                speed = sorted(speed_samples)[1]
                if speed >= 100.0:
                    speed = 99.9
                display.print(f"{speed:5.1f}")
                display.ampm = True
            else:
                display.print("----")
                display.ampm = False
        else:  # MODE_TIMER
            if timer_start is None:
                remaining = TIMER_DURATION
            else:
                remaining = max(0.0, TIMER_DURATION - (now - timer_start))
            minutes = int(remaining) // 60
            seconds = int(remaining) % 60
            display.print(f"{minutes:02d}:{seconds:02d}")
            display.colon = True
            # When the countdown reaches zero, flip to the speed view on the next tick.
            # timer_expired_handled ensures we only do this once per run, so pressing B
            # after the fact still lets you see the "00:00" state.
            if remaining <= 0 and timer_start is not None and not timer_expired_handled:
                timer_expired_handled = True
                current_mode = MODE_SPEED

    time.sleep(0.01)
