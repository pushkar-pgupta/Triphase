# Person 2 — Drone Control Scripts
## AirSim + Unreal Engine Python Control

---

## 📁 Files in This Folder

| File | Day | Purpose |
|---|---|---|
| `01_basic_flight.py` | Day 3 | Takeoff, hover, left/right/forward/backward movement, land |
| `02_waypoint_navigation.py` | Day 5 | Fly through a list of 3D waypoints automatically |
| `03_keyboard_control.py` | Bonus | Fly with keyboard keys (good for manual testing) |

---

## ⚙️ How the System Works

```
Your PC:
┌─────────────────────────────┐       TCP :41451
│  Python Script (this folder)│  ◄──────────────►  Unreal Engine + AirSim
│  airsim library             │                     (the simulation)
└─────────────────────────────┘
```

- **Unreal Engine** renders the world and physics
- **AirSim** is a plugin inside UE that exposes a drone API
- **Your Python script** connects to that API and sends commands
- They run **simultaneously** on the same machine (or same network)

---

## 🛠️ Setup (One-time)

### Step 1 — Install Python dependencies
```bash
pip install airsim numpy opencv-python keyboard
```

### Step 2 — Configure AirSim (settings.json)
AirSim reads a config file. Create/edit this file:

**Windows:**
```
C:\Users\<YourName>\Documents\AirSim\settings.json
```
**Linux/Mac:**
```
~/Documents/AirSim/settings.json
```

Paste this minimal config:
```json
{
  "SettingsVersion": 1.2,
  "SimMode": "Multirotor",
  "Vehicles": {
    "Drone1": {
      "VehicleType": "SimpleFlight",
      "X": 0, "Y": 0, "Z": 0,
      "Yaw": 0, "Pitch": 0, "Roll": 0
    }
  }
}
```

---

## 🚀 Running the Scripts

### Always do this first:
1. Open Unreal Engine with the AirSim project
2. Press **▶ Play** in UE to start the simulation
3. Wait until the drone appears in the UE viewport

### Then in a terminal:
```bash
# Day 3 — basic movements
python 01_basic_flight.py

# Day 5 — waypoint flight plan
python 02_waypoint_navigation.py

# Bonus — keyboard control
python 03_keyboard_control.py
```

---

## 🗺️ Coordinate System

AirSim uses **NED** (North-East-Down):

```
        +X (Forward / North)
        ↑
        │
-Y ←────┼────→ +Y
(Left)  │       (Right / East)
        │
     (Down = +Z, Up = -Z)
```

> **Key rule:** To go UP, use **negative Z** values.  
> Altitude of 5m = `z = -5` in AirSim coordinates.

---

## 🔧 Customizing Waypoints (02_waypoint_navigation.py)

Edit the `WAYPOINTS` list at the top of the file:
```python
WAYPOINTS = [
    (  0,   0, -5,  "Launch Hover"),   # x, y, z, label
    ( 10,   0, -5,  "Go North 10m"),
    ( 10,  10, -8,  "Go North+East, climb"),
    (  0,   0, -5,  "Return Home"),
]
```

Also tune these flight parameters:
```python
CRUISE_SPEED    = 3.0    # m/s - how fast between waypoints
WAYPOINT_RADIUS = 1.5    # m   - how close counts as "arrived"
HOVER_AT_WP     = 2.0    # s   - pause duration at each waypoint
```

---

## ❗ Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` | UE simulation is not running — press Play in UE first |
| Drone doesn't move | Check `enableApiControl(True)` and `armDisarm(True)` are called |
| Drone falls immediately | AirSim config may be wrong — check `settings.json` |
| `ModuleNotFoundError: airsim` | Run `pip install airsim` |
| Drone goes underground | Your Z value is positive — make it negative |

---

## 📤 Integration Notes (for Person 4)

The functions in `01_basic_flight.py` are all importable:

```python
# In the integration script (Person 4):
from drone_control.basic_flight import connect, takeoff, move_forward, land

client = connect()
takeoff(client)
move_forward(client, distance_m=10)
land(client)
```
