# Velocidev — Firmware Plan

Overview of all the CircuitPython code to be written for the Velocidev GPS speed tracker, with a phased TODO list.

## Goal

A mast-mounted GPS speed display for dinghy sailing. Shows speed over ground in knots on a 1.2" 7-segment LED, updates ~1Hz, logs the session to a microSD card. Runs on an RP2040 Adalogger Feather with a GPS FeatherWing and a HT16K33-driven LED backpack.

## Target file layout on `CIRCUITPY`

```
CIRCUITPY/
├── code.py                 # Main sailing firmware (production)
├── boot.py                 # (optional) USB drive / SD card mode config
├── settings.toml           # User-tunable constants (units, brightness, log format)
├── lib/                    # CircuitPython libraries (already installed)
└── tests/                  # Individual hardware verification scripts
    ├── test_blink.py       # Onboard LED (done)
    ├── test_display.py     # 7-segment: light all segments, count 0-9999
    ├── test_gps.py         # Dump raw NMEA to serial, then parsed fields
    ├── test_oled.py        # 128x64 OLED "hello world" + bounce animation
    └── test_sdcard.py      # Mount SD, write and read back a test file
```

To run any `tests/*.py` file, copy its contents into `code.py` on the drive (CircuitPython only auto-runs `code.py`).

---

## Phased TODO

### Phase 1 — Hardware verification

Confirm every component works in isolation before wiring them together in the main loop. Each is a small script (~20-40 lines).

- [x] **1.1 Blink test** — onboard LED blinks every 500ms, "blink" prints to serial. *Done.*
- [x] **1.2 7-segment display test** — initialize HT16K33 over I2C, light all segments briefly, then count 0000 → 9999. Verify STEMMA QT wiring and I2C address. *Done.*
- [x] **1.3 + 1.4 GPS test (combined, with OLED display)** — read from GPS FeatherWing's UART at 9600 baud, use `adafruit_gps` to parse NMEA, show fix status / sat count / speed / UTC time on the OLED. Runnable outdoors on battery without a serial console. *Test file: `test_gps_oled.py`. Done — confirmed 7 sat fix outdoors, speed tracks walking pace (~4 kt).*
- [x] **1.5 OLED test** — draw "hello velocidev" text and a bouncing pixel. Confirms OLED FeatherWing and I2C bus sharing with the LED display. *Done. Rotation=90 gives correct landscape orientation.*
- [ ] **1.6 SD card test** — mount the built-in microSD, write a timestamped test line, read it back. Confirms Adalogger's SD circuit. *No soldering required — SD slot is on the Feather itself.*

### Phase 2 — Core sailing firmware (main loop)

The minimum viable product: GPS → display.

- [x] **2.1 GPS reader module** — inlined into `code.py` rather than a separate module (the whole thing is ~40 lines of setup + a loop; extraction would add cost without benefit at this size).
- [x] **2.2 Display formatter** — render speed on the 7-segment as `XX.X` (e.g., `5.3` becomes ` 5.3`, `12.7` becomes `12.7`). Show dashes `----` when no fix.
- [x] **2.3 Main loop v1** — every 500ms: poll GPS, format speed, update display. Blink onboard LED as a "still alive" indicator.
- [x] **2.4 Startup sequence** — on boot: brief self-test (all segments lit for 1 sec) then `----` until GPS fix.

### Phase 3 — Session features

Features that make it actually useful for improving sailing.

- [ ] **3.1 Max speed tracking** — track the max speed seen this session. Persist in RAM.
- [ ] **3.2 Display mode toggle** — on-startup or timed rotation: alternate between current speed and session max. Configurable in `settings.toml`.
- [ ] **3.3 SD card logging** — every second (or configurable), append CSV row: `timestamp_iso, speed_knots, lat, lon, course_deg, sats`. New file per session, named by GPS timestamp on first fix.
- [ ] **3.4 Session detection** — start a new log when GPS speed exceeds a threshold (e.g., 1 knot for 10 sec). Close cleanly when speed stays below threshold for 5 minutes (auto-save log).

### Phase 4 — Polish and reliability

Things that make it robust for a full day of sailing.

- [ ] **4.1 Display brightness control** — HT16K33 supports 16 brightness levels. Default max for daylight, add dim mode. Consider a light sensor later, or manual button on the enclosure.
- [ ] **4.2 Battery voltage monitoring** — read Feather's `board.VOLTAGE_MONITOR` pin, warn on 7-segment (`bAtt` message) below ~3.5V.
- [ ] **4.3 Error handling** — catch and log GPS timeouts, I2C failures, SD write errors. Display error codes (`E001`, etc.) rather than crashing.
- [ ] **4.4 Watchdog / auto-recovery** — if the loop stalls, reset gracefully. RP2040 has a hardware watchdog available in CircuitPython 9+.

### Phase 5 — Nice-to-haves (optional, later)

- [ ] **5.1 Configurable units** — knots (default) / mph / km/h switchable via `settings.toml`.
- [ ] **5.2 Course over ground** — display heading briefly on a button press.
- [ ] **5.3 GPX export** — convert CSV logs to GPX format so they can be viewed in mapping tools (Strava, Google Earth). Could be a separate desktop Python script rather than on-board.
- [ ] **5.4 OLED debug overlay (dev only)** — when OLED is connected, show extra info (sat count, HDOP, battery V) that would clutter the main 7-segment.

---

## Non-goals (explicitly out of scope for now)

- Heel angle measurement — Adalogger has no IMU. Would need to add an I2C accelerometer breakout.
- Wireless data transfer — RP2040 has no WiFi/BT. Session review happens by pulling the microSD.
- Race start timer — could be added in Phase 5 if wanted.
- Waypoint navigation — this is a speed instrument, not a chartplotter.
