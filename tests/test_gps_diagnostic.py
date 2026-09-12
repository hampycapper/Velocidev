"""
Velocidev Test 1.3b - GPS UART byte-level diagnostic

Purpose:
- Detect whether the Feather is receiving ANY bytes from the GPS at all
- Distinguish "nothing arriving" from "wrong baud rate / garbled" from
  "everything looks fine at the byte level but parser can't handle it"

Displays on OLED (128x64):
    GPS Diagnostic
    Bytes: NNNN         <- total bytes received since boot
    Lines: NN           <- complete lines (terminated by \\n)
    <last $ line>       <- last NMEA sentence seen (truncated)
    hex: XX XX XX XX    <- first bytes of most recent chunk

Diagnosis guide:

  Bytes = 0 forever:
    - GPS is not sending, OR wiring/pins wrong.
    - Check the FIX LED on the GPS wing. If it's dark, GPS isn't powered.
    - If FIX LED blinks but Bytes stays 0, the UART connection is broken:
        * FeatherWing not seated
        * Cold solder joint on TX/RX header pins
        * Wrong pin definition (should be board.TX, board.RX)

  Bytes grows but Lines = 0 and hex looks like random garbage
  (e.g., "FF EE C3 A1..."):
    - Wrong baud rate. GPS is set to something other than 9600.
    - Try 4800 or 38400 by editing baudrate= below.

  Bytes grows, Lines grows, "$GN..." or "$GP..." lines visible:
    - GPS is healthy and transmitting. Any issues are in the parsing layer.
    - Go back to test_gps_oled.py.
"""

import time
import board
import busio
import displayio
from i2cdisplaybus import I2CDisplayBus
from adafruit_displayio_sh1107 import SH1107
from adafruit_display_text import label
import terminalio

# --- OLED setup ---
displayio.release_displays()
i2c = board.I2C()
display_bus = I2CDisplayBus(i2c, device_address=0x3C)
display = SH1107(display_bus, width=128, height=64, rotation=90)

# --- UART setup ---
# If Bytes stays 0 with the FIX LED blinking, try changing baudrate.
BAUD = 9600  # default for MTK3333 / PA1616D
uart = busio.UART(board.TX, board.RX, baudrate=BAUD, timeout=0.1)

# --- OLED UI ---
scene = displayio.Group()
title = label.Label(terminalio.FONT, text=f"GPS Diag {BAUD}", color=0xFFFFFF, x=2, y=6)
bytes_line = label.Label(terminalio.FONT, text="Bytes: 0", color=0xFFFFFF, x=2, y=20)
lines_line = label.Label(terminalio.FONT, text="Lines: 0", color=0xFFFFFF, x=2, y=32)
last_nmea = label.Label(terminalio.FONT, text="no NMEA yet", color=0xFFFFFF, x=2, y=44)
hex_line = label.Label(terminalio.FONT, text="hex: --", color=0xFFFFFF, x=2, y=56)

for item in (title, bytes_line, lines_line, last_nmea, hex_line):
    scene.append(item)
display.root_group = scene

# --- Diagnostics loop ---
total_bytes = 0
total_lines = 0
buffer = b""
last_dollar = "no NMEA yet"
last_hex = "--"
last_update = time.monotonic()

while True:
    data = uart.read(64)
    if data:
        total_bytes += len(data)
        # Capture hex of first bytes to detect wrong-baud garbage
        last_hex = " ".join(f"{b:02X}" for b in data[:4])
        buffer += data

        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            total_lines += 1
            try:
                text = line.decode("ascii").strip()
                if text.startswith("$"):
                    last_dollar = text[:16]  # first 16 chars to fit on OLED
            except UnicodeError:
                pass

    now = time.monotonic()
    if now - last_update >= 0.5:
        last_update = now
        bytes_line.text = f"Bytes: {total_bytes}"
        lines_line.text = f"Lines: {total_lines}"
        last_nmea.text = last_dollar
        hex_line.text = f"hx:{last_hex}"

    time.sleep(0.01)
