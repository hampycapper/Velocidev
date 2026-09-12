"""
Velocidev Test 1.6 - microSD card verification (no soldering required)

Verifies:
- SD card is inserted and recognized
- FAT filesystem mounts
- We can write, read, and list files
- SD circuit on the Adalogger works

Physical setup:
- Insert a FAT32-formatted microSD card into the Adalogger's slot
- Feather powered via USB-C
- No soldering required for this test

Expected behavior when running:
  1. Serial prints "SD card test starting"
  2. Mounts the card at /sd
  3. Writes a test file with a timestamp
  4. Reads it back and prints contents
  5. Lists all files in /sd
  6. Prints total/free space
  7. Loops appending a new line to a log every 2 seconds

If it fails, check:
  - Card is inserted fully (feels a click)
  - Card is FAT32 formatted (Windows: right-click > Format > FAT32)
  - Card size is <= 32GB (larger cards may need to be reformatted as FAT32)
"""

import time
import board
import busio
import digitalio
import sdcardio
import storage
import os

print("SD card test starting")

# The Adalogger has dedicated pins for its SD card slot.
# board.SD_SPI() returns a preconfigured SPI bus using those pins.
spi = board.SD_SPI()
cs = board.SD_CS

sd = sdcardio.SDCard(spi, cs)
vfs = storage.VfsFat(sd)
storage.mount(vfs, "/sd")

print("SD card mounted at /sd")

# --- Write a test file ---
test_path = "/sd/velocidev_test.txt"
boot_time = time.monotonic()
with open(test_path, "w") as f:
    f.write("Velocidev SD card test\n")
    f.write(f"Boot time: {boot_time:.2f} sec\n")
    f.write("If you can read this, SD writes work.\n")

print(f"Wrote {test_path}")

# --- Read it back ---
with open(test_path, "r") as f:
    print("--- File contents ---")
    print(f.read())
    print("--- End file ---")

# --- List all files ---
print("Files on SD card:")
for entry in os.listdir("/sd"):
    stat = os.stat(f"/sd/{entry}")
    size = stat[6]
    print(f"  {entry}  ({size} bytes)")

# --- Space info ---
statvfs = os.statvfs("/sd")
block_size = statvfs[0]
total_blocks = statvfs[2]
free_blocks = statvfs[3]
total_mb = (block_size * total_blocks) / (1024 * 1024)
free_mb = (block_size * free_blocks) / (1024 * 1024)
print(f"SD card: {total_mb:.1f} MB total, {free_mb:.1f} MB free")

# --- Loop: append to a log file every 2 seconds ---
log_path = "/sd/velocidev_log.txt"
line = 0
print(f"Appending to {log_path} every 2 seconds (Ctrl+C to stop)")
while True:
    line += 1
    with open(log_path, "a") as f:
        f.write(f"{line},{time.monotonic():.2f}\n")
    print(f"Wrote line {line}")
    time.sleep(2)
