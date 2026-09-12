# Velocidev — Future Hardware Buy List

Additions we've talked about but haven't wired up yet. Ordered by priority.

---

## 1. Compass + heel angle (IMU)

A 9-DOF IMU gives us three magnetometer axes (compass heading) *and* three accelerometer axes (tilt / heel / trim). To get a stable **tilt-compensated compass heading** — i.e. a real heading number that doesn't wander when the boat heels — you need both plus the math that fuses them.

### Option A — Smart sensor (recommended, "just works")

| Item | Part | Cost | Notes |
|------|------|------|-------|
| IMU with on-chip sensor fusion | **Adafruit BNO085 9-DOF breakout** (#4754) | ~$25 | Runs its own fusion firmware. Reports Euler angles (yaw/pitch/roll) directly — you don't write filter code. STEMMA QT connectors, plug straight into the existing I2C chain. |
| STEMMA QT cable | 50mm or 100mm | ~$1 | Daisy-chain onto the OLED + 7-segment I2C bus. |

Alternative smart sensor:
- **Adafruit BNO055 breakout** (#2472) — older, ~$30, similar features. BNO085 has cleaner CircuitPython library and lower power draw.

### Option B — Raw sensors + do-it-yourself fusion (cheaper, more code)

| Item | Part | Cost | Notes |
|------|------|------|-------|
| 6-DOF IMU (accel + gyro) | **Adafruit LSM6DSOX** (#4438) | ~$8 | |
| Magnetometer | **Adafruit LIS3MDL** (#4479) | ~$6 | |
| STEMMA QT cable | | ~$1 | |

You'd have to implement the fusion math yourself (Madgwick or Mahony filter, both well-documented). Half the cost, several evenings of extra work, and calibration is more manual. Not recommended unless the DIY is the point.

### Installation notes for either option

- Mount the IMU **rigidly to the boat frame**, not to the enclosure lid — the lid flexes.
- **Align axes clearly**: pick one axis for "boat forward" and mark it. All heading and heel calculations depend on knowing the sensor's orientation vs the boat's.
- **Keep away from ferrous metal and power wires** (motors, big batteries, steel rigging). Not usually a problem on a dinghy with a small LiPo, but worth checking with a real compass before final mount.
- **Calibrate on first use.** BNO085 does hard-iron calibration automatically as the boat moves. Raw magnetometers need a one-time figure-8 calibration routine.
- Only useful when the boat is moving (or the sensor is level enough for heel to be meaningful) — GPS course-over-ground remains the source of truth for direction of travel.

---

## 2. Reed switches (for waterproof mode buttons)

Replaces the OLED FeatherWing buttons once the build is in an enclosure. See earlier conversation about placement (~3cm apart, mark spots on the outside).

| Item | Part | Cost | Notes |
|------|------|------|-------|
| Reed switches (2) | Adafruit #375 pre-wired *or* bulk glass reed switches ~15-25 AT | $2-8 | Pre-wired is easier if not soldering; bulk reeds are cheaper and smaller. |
| Neodymium magnet | 6-10mm disk, N42 grade | ~$1 | Keep on a lanyard so it doesn't wander. Any craft/hardware store or scavenged from a dead hard drive. |

---

## 3. Optional but nice

| Item | Part | Cost | Why |
|------|------|------|-----|
| External active GPS antenna | u.FL-connector patch antenna | ~$10 | If the internal antenna is buried inside an enclosure that blocks reception, an external antenna on top improves fix reliability. Not always needed. |
| Light sensor | Adafruit VEML7700 (#4162) | ~$5 | Auto-dim the 7-segment for readability in changing light (bright in sun, dim at dusk). Currently we only support manual brightness. |
| Waterproof cable gland | M8 or M10 | ~$2 each | For any wire that has to leave the enclosure (external antenna, charging port cover). |

---

## What we already have

Just so future-you doesn't re-buy:

- Adafruit Feather RP2040 Adalogger (microSD built in)
- Adafruit Ultimate GPS FeatherWing
- Adafruit 1.2" 4-digit 7-segment display + HT16K33 backpack
- Adafruit 128x64 OLED FeatherWing (SH1107) — currently used for its A/B/C buttons
- STEMMA QT cables
- LiPo battery + USB-C charger (or on the wish list — check what's on hand)
