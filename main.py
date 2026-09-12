"""
Velocidev - main sailing firmware v1

Minimum viable product for the mast-mounted speed display:
- Reads GPS speed over ground at 1 Hz via the Ultimate GPS FeatherWing
- Shows speed in knots on the 1.2" 4-digit 7-segment LED (HT16K33 backpack)
- Displays ---- until a GPS fix is acquired
- Blinks the onboard LED as a heartbeat so we can tell the loop is alive

Hardware:
- Adafruit Feather RP2040 Adalogger
- Adafruit Ultimate GPS FeatherWing (stacked)
- Adafruit 1.2" 4-digit 7-segment LED (HT16K33) via STEMMA QT

Display format:
- Speed under 10 kt shown blank-padded, e.g. " 5.3"
- Speed 10-99.9 kt shown as XX.X, e.g. "12.7"
- No fix: "----"
- Boot self-test: "8.8.8.8" (every segment lit) for one second
"""

import time
import board
import busio
import digitalio
import adafruit_gps
from adafruit_ht16k33.segments import BigSeg7x4

# --- Hardware setup ---
i2c = board.I2C()
display = BigSeg7x4(i2c)
display.brightness = 1.0

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0.1)
gps = adafruit_gps.GPS(uart, debug=False)
# Ask for RMC + GGA at 1 Hz. RMC gives speed over ground; GGA gives sats/fix.
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# --- Boot self-test ---
display.fill(1)
time.sleep(1.0)
display.fill(0)
display.print("----")

# --- Main loop ---
UPDATE_INTERVAL = 0.5

last_update = time.monotonic()
# Sliding window of the last 3 raw speed samples for median-of-3 filtering.
# Removes single-sample GPS jitter spikes at ~1 sample of lag.
speed_samples = [0.0, 0.0, 0.0]

while True:
    gps.update()

    now = time.monotonic()
    if now - last_update >= UPDATE_INTERVAL:
        last_update = now
        led.value = not led.value

        if gps.has_fix and gps.speed_knots is not None:
            speed_samples[0] = speed_samples[1]
            speed_samples[1] = speed_samples[2]
            speed_samples[2] = gps.speed_knots
            speed = sorted(speed_samples)[1]
            if speed >= 100.0:
                speed = 99.9
            display.print(f"{speed:5.1f}")
            # Top-right AM/PM dot as a "tenths digit" reminder
            display.ampm = True
        else:
            display.print("----")
            display.ampm = False

    time.sleep(0.01)
