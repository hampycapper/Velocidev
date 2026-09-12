"""
Velocidev Test 1.2 - 7-segment display verification

Verifies:
- I2C bus (STEMMA QT) is working
- HT16K33 backpack responds at expected address (0x70)
- All 4 digits work
- All segments in each digit work
- Decimal points work
- Brightness control works

Expected behavior when running:
  1. Serial console prints "Display test starting"
  2. All segments light up (shows 8.8.8.8) for 2 seconds
  3. Each digit position tested one at a time (shows 8..., .8.., ..8., ...8)
  4. Fast count from 0 to 9999
  5. Brightness sweep from dim to bright, on a fixed "88.88" pattern
  6. Loops the count + brightness sweep forever

If the display stays blank or you see an OSError in serial, check:
  - STEMMA QT cable seated in both connectors
  - Display+backpack solder joints
  - I2C address (default 0x70; can be changed via solder jumpers on backpack)
"""

import time
import board
from adafruit_ht16k33.segments import BigSeg7x4

print("Display test starting")

i2c = board.I2C()
display = BigSeg7x4(i2c)
display.brightness = 1.0

print("Display initialized. If you see this and no error, I2C is working.")

def all_on():
    """Light every segment on every digit, including decimal points."""
    display.fill(1)

def all_off():
    display.fill(0)

def show_each_digit():
    """Test each digit position by lighting one at a time."""
    for pos in range(4):
        all_off()
        display.set_digit_raw(pos, 0xFF)  # all segments in this digit
        time.sleep(0.5)

def count_fast():
    """Sweep from 0 to 9999 quickly to visually confirm all digits work."""
    for n in range(0, 10000, 7):
        display.print(n)
        time.sleep(0.005)

def brightness_sweep():
    """Fade from dim to full brightness on a fixed pattern."""
    display.print("88.88")
    for step in range(16):
        display.brightness = step / 15.0
        time.sleep(0.1)
    for step in range(15, -1, -1):
        display.brightness = step / 15.0
        time.sleep(0.1)
    display.brightness = 1.0

# --- Startup self-test ---
print("Step 1: all segments on (should show 8.8.8.8)")
all_on()
time.sleep(2)

print("Step 2: each digit tested individually")
show_each_digit()

# --- Main loop ---
loop = 0
while True:
    loop += 1
    print(f"Loop {loop}: count 0-9999")
    count_fast()

    print(f"Loop {loop}: brightness sweep")
    brightness_sweep()

    time.sleep(1)
