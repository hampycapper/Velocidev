"""
Velocidev Test 1.5 - OLED display verification (no soldering required)

Verifies:
- I2C bus (STEMMA QT) is working
- SH1107 driver responds
- Text and pixel drawing work

Physical setup:
- STEMMA QT cable from Feather to OLED FeatherWing
- Feather powered via USB-C
- No soldering required for this test

Expected behavior when running:
  1. Serial console prints "OLED test starting"
  2. OLED shows "Hello Velocidev" and a version/status line
  3. A pixel bounces around the screen indefinitely
  4. Serial prints frame counter every second

If the display stays blank or you see an OSError, check:
  - STEMMA QT cable seated in both connectors
  - I2C address (default 0x3C for this board)
"""

import time
import board
import displayio
from i2cdisplaybus import I2CDisplayBus
from adafruit_displayio_sh1107 import SH1107
from adafruit_display_text import label
import terminalio
import vectorio

print("OLED test starting")

# Release any previously configured displays (safe to run multiple times)
displayio.release_displays()

i2c = board.I2C()
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
display = SH1107(display_bus, width=128, height=64, rotation=90)

print("SH1107 initialized. If you see this and no error, I2C is working.")

# Build a scene: title text + subtitle + a bouncing dot
scene = displayio.Group()

title = label.Label(
    terminalio.FONT,
    text="Hello Velocidev",
    color=0xFFFFFF,
    x=8,
    y=10,
)
scene.append(title)

subtitle = label.Label(
    terminalio.FONT,
    text="OLED test OK",
    color=0xFFFFFF,
    x=8,
    y=24,
)
scene.append(subtitle)

# A small filled square that will move around
palette = displayio.Palette(1)
palette[0] = 0xFFFFFF
dot = vectorio.Rectangle(pixel_shader=palette, width=4, height=4, x=0, y=40)
scene.append(dot)

display.root_group = scene

# Bounce the dot around in the bottom half of the screen
x, y = 0, 40
dx, dy = 1, 1
frame = 0
last_report = time.monotonic()

while True:
    x += dx
    y += dy
    if x <= 0 or x >= 128 - 4:
        dx = -dx
    if y <= 32 or y >= 64 - 4:
        dy = -dy
    dot.x = x
    dot.y = y

    frame += 1
    now = time.monotonic()
    if now - last_report >= 1.0:
        print(f"Frame {frame}, dot at ({x}, {y})")
        last_report = now

    time.sleep(0.02)
