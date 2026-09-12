"""
Velocidev Test 1.3 + 1.4 combined - GPS with OLED status display

Verifies:
- GPS FeatherWing is powered and transmitting
- UART wiring is correct (Feather TX/RX at 9600 baud)
- adafruit_gps library can parse the NMEA stream
- We can extract fix status, satellite count, speed, and time
- Everything is visible on the OLED for outdoor testing (no serial console needed)

Physical setup:
- GPS FeatherWing stacked on the Feather
- OLED FeatherWing connected via STEMMA QT cable
- Feather powered via USB-C or LiPo
- Take it outside with sky view

OLED display layout (128x64 landscape):
    Velocidev GPS
    Fix: YES/no
    Sats: N
    Spd: X.X kt
    UTC: HH:MM:SS

What to watch for:
  - "Fix: no" for the first 30-60 seconds outdoors (cold start)
  - Sats count climbing from 0 as satellites are acquired
  - "Fix: YES" once we have a valid position
  - Speed will be near 0 when stationary; walk around to see it move
  - UTC clock starts updating as soon as we have satellites (even before fix)

Onboard NeoPixel: green = happy, red = error. If red, plug in USB and check serial.
"""

import time
import board
import busio
import displayio
from i2cdisplaybus import I2CDisplayBus
from adafruit_displayio_sh1107 import SH1107
from adafruit_display_text import label
import terminalio
import adafruit_gps

# --- OLED setup ---
displayio.release_displays()
i2c = board.I2C()
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
display = SH1107(display_bus, width=128, height=64, rotation=90)

# --- GPS setup ---
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0.1)
gps = adafruit_gps.GPS(uart, debug=False)
# Ask GPS for RMC + GGA sentences at 1 Hz (defaults are usually fine but let's be explicit)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
gps.send_command(b"PMTK220,1000")

# --- OLED UI ---
scene = displayio.Group()

title = label.Label(terminalio.FONT, text="Velocidev GPS", color=0xFFFFFF, x=2, y=6)
fix_line = label.Label(terminalio.FONT, text="Fix: ...", color=0xFFFFFF, x=2, y=20)
sats_line = label.Label(terminalio.FONT, text="Sats: 0", color=0xFFFFFF, x=2, y=32)
speed_line = label.Label(terminalio.FONT, text="Spd: --.-", color=0xFFFFFF, x=2, y=44)
time_line = label.Label(terminalio.FONT, text="UTC: --:--:--", color=0xFFFFFF, x=2, y=56)

for item in (title, fix_line, sats_line, speed_line, time_line):
    scene.append(item)

display.root_group = scene

# --- Main loop ---
last_update = time.monotonic()

while True:
    # Feed GPS parser as fast as possible (non-blocking)
    gps.update()

    now = time.monotonic()
    if now - last_update >= 0.5:
        last_update = now

        if gps.has_fix:
            fix_line.text = "Fix: YES"
            speed = gps.speed_knots if gps.speed_knots is not None else 0.0
            speed_line.text = f"Spd: {speed:4.1f} kt"
        else:
            fix_line.text = "Fix: no"
            speed_line.text = "Spd: --.- kt"

        sats = gps.satellites if gps.satellites is not None else 0
        sats_line.text = f"Sats: {sats}"

        if gps.timestamp_utc is not None:
            t = gps.timestamp_utc
            time_line.text = f"UTC: {t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d}"

    time.sleep(0.01)
