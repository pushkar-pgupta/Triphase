"""
Person 2 - Drone Control | Bonus / Testing Tool
Script: 03_keyboard_control.py

PURPOSE:
    Fly the drone MANUALLY using keyboard keys — great for testing
    the simulation before automating anything.

CONTROLS:
    T = Takeoff       L = Land
    W = Forward       S = Backward
    A = Left          D = Right
    Q = Turn Left     E = Turn Right
    R = Go Up         F = Go Down
    P = Print Position
    X = Emergency land + quit

HOW TO RUN:
    pip install airsim keyboard
    python 03_keyboard_control.py       (may need: sudo on Linux)

NOTE:
    The `keyboard` library captures keys globally (system-wide).
    Run this script in a terminal. Press keys while the terminal is focused.
"""

import airsim
import time

try:
    import keyboard
except ImportError:
    print("[ERROR] Install the keyboard library: pip install keyboard")
    exit(1)

# ─────────────────────────────────
STEP_M  = 2.0    # meters per keypress
SPEED   = 2.0    # m/s
YAW_DEG = 30     # degrees per Q/E press
ALTITUDE = 5.0   # takeoff altitude in meters
# ─────────────────────────────────

client = None
airborne = False


def connect():
    global client
    print("[INFO] Connecting ...")
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    print("[OK]   Connected. Use keys to fly. Press X to quit.")


def do_takeoff():
    global airborne
    if airborne:
        print("[SKIP] Already airborne")
        return
    print("[INFO] Takeoff ...")
    client.takeoffAsync().join()
    client.moveToZAsync(-ALTITUDE, velocity=2).join()
    airborne = True
    print("[OK]   Airborne")


def do_land():
    global airborne
    print("[INFO] Landing ...")
    client.landAsync().join()
    airborne = False
    print("[OK]   Landed")


def get_pos():
    return client.getMultirotorState().kinematics_estimated.position


def move(vx=0, vy=0, vz=0):
    """Move for a fixed duration at given velocity."""
    if not airborne:
        print("[SKIP] Not airborne — press T to take off first")
        return
    duration = STEP_M / SPEED
    client.moveByVelocityAsync(vx, vy, vz, duration).join()
    client.hoverAsync()


def yaw(degrees):
    if not airborne:
        return
    speed = 45  # deg/s
    client.rotateByYawRateAsync(
        yaw_rate=speed if degrees > 0 else -speed,
        duration=abs(degrees) / speed
    ).join()


if __name__ == "__main__":
    connect()

    print("""
──────────────────────────────────
  KEYBOARD DRONE CONTROL ACTIVE
──────────────────────────────────
  T       Takeoff
  L       Land
  W/S     Forward / Backward
  A/D     Left / Right
  R/F     Up / Down
  Q/E     Yaw Left / Right
  P       Print position
  X       Emergency land + quit
──────────────────────────────────
""")

    running = True

    keyboard.add_hotkey('t', do_takeoff)
    keyboard.add_hotkey('l', do_land)
    keyboard.add_hotkey('w', lambda: move(vx=SPEED))
    keyboard.add_hotkey('s', lambda: move(vx=-SPEED))
    keyboard.add_hotkey('d', lambda: move(vy=SPEED))
    keyboard.add_hotkey('a', lambda: move(vy=-SPEED))
    keyboard.add_hotkey('r', lambda: move(vz=-SPEED))
    keyboard.add_hotkey('f', lambda: move(vz=SPEED))
    keyboard.add_hotkey('q', lambda: yaw(-YAW_DEG))
    keyboard.add_hotkey('e', lambda: yaw(YAW_DEG))
    keyboard.add_hotkey('p', lambda: print(f"  Position: {get_pos()}"))

    def emergency_exit():
        global running
        print("\n[X] Emergency stop — landing ...")
        if airborne:
            client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
        running = False

    keyboard.add_hotkey('x', emergency_exit)

    while running:
        time.sleep(0.1)

    print("[DONE] Controller exited.")
