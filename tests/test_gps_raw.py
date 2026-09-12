"""
Velocidev Test 1.3 - GPS raw NMEA dump

Verifies:
- GPS FeatherWing is powered and transmitting
- UART wiring is correct (Feather TX/RX)
- Raw NMEA sentences arrive at the Feather

Physical setup:
- GPS FeatherWing stacked on the Feather (or wired to TX/RX + 3V/GND)
- Feather powered via USB-C
- Ideally hold near a window with sky view, or test outside

Expected behavior:
  1. Serial prints "GPS raw test starting"
  2. Within a few seconds, lines starting with $GP or $GN appear
     ($GPRMC, $GPGGA, $GPGSV, etc. or $GN variants for multi-GNSS)
  3. GPS "FIX" LED on the FeatherWing blinks ~1 Hz until a fix, then
     blinks briefly every ~15 seconds once fixed
  4. Once fixed, the RMC sentence will contain your position

What to look for:
  - $GPRMC / $GNRMC:
      $GNRMC,hhmmss.ss,A,lat,N/S,lon,E/W,speed_knots,course,ddmmyy,,,mode*checksum
      The 'A' = valid fix ('V' = void/no fix)
      speed_knots is the speed over ground - this is what we want!
  - $GPGGA / $GNGGA:
      Contains fix quality, satellite count, HDOP

If nothing appears:
  - Check GPS FeatherWing is fully seated on the Feather headers
  - Check the FIX LED - if it's blinking, GPS is running (just no data reaching Feather)
  - Confirm baud rate is 9600 (default for PA1616D/MTK3333)

If lines are garbled (mojibake):
  - Wrong baud rate - try 4800 or 38400
"""

import time
import board
import busio

print("GPS raw test starting")
print("Waiting for GPS output on TX/RX at 9600 baud...")
print("(Sentences typically start appearing within a few seconds)")
print()

# The GPS FeatherWing's UART connects to the Feather's TX/RX pins.
# board.TX = Feather TX (GPS RX)
# board.RX = Feather RX (GPS TX)
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=0.1)

buffer = b""
line_count = 0
last_status = time.monotonic()
saw_fix = False

while True:
    data = uart.read(64)
    if data:
        buffer += data
        # Process any complete lines (terminated by \n)
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            try:
                text = line.decode("ascii").strip()
            except UnicodeError:
                text = f"<garbled: {line!r}>"

            if text:
                line_count += 1
                print(text)

                # Detect a valid fix (RMC status 'A')
                if ("RMC" in text) and (",A," in text) and not saw_fix:
                    print("*** GPS FIX ACQUIRED ***")
                    saw_fix = True

    # Periodic status ping so we know the test is alive
    now = time.monotonic()
    if now - last_status >= 5.0:
        print(f"[status: {line_count} lines seen, fix={saw_fix}]")
        last_status = now

    time.sleep(0.01)
