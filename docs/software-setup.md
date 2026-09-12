# Velocidev — Software Setup (Windows)

Setup guide for the RP2040 Adalogger Feather + GPS FeatherWing + 1.2" 7-segment LED display + optional 128x64 OLED FeatherWing build.

We are using **CircuitPython** (Adafruit's Python variant, designed specifically for this hardware). No compile step — edit `code.py` on the board and it runs immediately.

---

## Step 1 — Install CircuitPython on the Feather

1. Go to `circuitpython.org/board/adafruit_feather_rp2040_adalogger` and download the latest stable `.uf2` file
2. **Hold the BOOT button** on the Feather while plugging it into your PC via USB-C
3. Release BOOT after ~2 seconds — the board mounts as a USB drive named `RPI-RP2`
4. **Drag the `.uf2` file onto that drive**
5. The board reboots automatically and remounts as `CIRCUITPY` — that is your code drive

The board now runs Python and appears as a folder in File Explorer.

---

## Step 2 — Install a code editor

**Recommended: Mu Editor** (`codewith.mu`). Made specifically for CircuitPython. Has a built-in serial console for debugging.

Alternatives:
- **Thonny** (`thonny.org`) — more capable if you already know Python
- **VS Code** with the "CircuitPython v2" extension — full IDE

Install Mu with the standard Windows installer. When it asks for a mode, pick **"Adafruit CircuitPython"** (NOT "ESP MicroPython" — that is for ESP boards running MicroPython, which is a different Python variant).

---

## Step 3 — Check your CircuitPython version

Before downloading libraries, find out which CircuitPython version is on the board so you can grab the matching bundle.

**Easiest way**: open `boot_out.txt` on the `CIRCUITPY` drive. The first line looks like:

```
Adafruit CircuitPython 10.2.0 on 2026-...; Adafruit Feather RP2040 Adalogger with rp2040
```

Match the **major version** to the library bundle (CP 10.x → Bundle 10.x). Minor version does not need to match. **This project targets CircuitPython 10.x** — many online tutorials are for older versions and use APIs that no longer exist (see "CP 10.x API notes" at the end of this doc).

---

## Step 4 — Install the libraries

### Option A — Manual (simpler for first-time setup)

Download the **CircuitPython Library Bundle** from `circuitpython.org/libraries` matching your CP major version. Unzip it.

From the unzipped `lib/` folder, copy these into a `lib/` folder on `CIRCUITPY`:

- `adafruit_gps.mpy`
- `adafruit_ht16k33/` (whole folder — drives the 1.2" 7-segment)
- `adafruit_bus_device/` (dependency)
- `adafruit_register/` (dependency)
- `adafruit_displayio_sh1107.mpy` (for the 128x64 OLED FeatherWing — uses SH1107 driver, NOT SSD1306)
- `adafruit_display_text/` (folder — for OLED text rendering)
- `adafruit_sdcard.mpy` (for logging to microSD later)

**Note**: `i2cdisplaybus`, `displayio`, `vectorio`, `terminalio`, and `fourwire` are all built into CircuitPython 10.x — no library install needed for those.

### Option B — `circup` (automated)

Requires Python installed on Windows first (`python.org`, tick "Add to PATH" during install).

```powershell
pip install circup
circup install adafruit_gps adafruit_ht16k33 adafruit_displayio_sh1107 adafruit_display_text adafruit_sdcard
```

---

## Step 5 — First test

**IMPORTANT**: the file MUST be named `code.py` (or `main.py`). CircuitPython only auto-runs those specific filenames — anything else is ignored.

Save this as `code.py` on the `CIRCUITPY` drive:

```python
import board
import digitalio
import time

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
    print("blink")
```

In Mu, click **"Serial"** to open the REPL console. You should see:
- The onboard LED blinking every half-second
- `blink` printing in the console every second

If that works, the toolchain is fully set up.

---

## Troubleshooting

- **Code not running?** Check the filename is exactly `code.py`. Other names are ignored.
- **NeoPixel color codes**: green = happy, yellow = safe mode, red = error, blue = booting. If red, check the serial console for the error message.
- **Antivirus** sometimes flags rapid writes to `CIRCUITPY`. If saving feels slow or files vanish, add an exception for the drive.
- **Serial port drivers** are usually auto-installed. If Mu cannot see the board, unplug/replug and wait a few seconds.
- **Do not "safely eject"** the `CIRCUITPY` drive — just save files and they run. Windows will occasionally warn about "unexpected removal" if the board resets; ignore it.

---

## CP 10.x API notes

This project targets **CircuitPython 10.x**. Several APIs changed between CP 8.x/9.x and 10.x; many online tutorials still use the old names. If you copy example code from the internet and get `AttributeError` or `ImportError`, check these:

| Old (CP 8.x/9.x) | New (CP 10.x) |
|------------------|---------------|
| `displayio.I2CDisplay(bus, ...)` | `from i2cdisplaybus import I2CDisplayBus` then `I2CDisplayBus(bus, ...)` |
| `displayio.FourWire(...)` | `from fourwire import FourWire` then `FourWire(...)` |
| `display.show(group)` | `display.root_group = group` |

Always prefer the CP 10.x-native API in new code.
