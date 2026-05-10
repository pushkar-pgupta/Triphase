"""
Person 2 - Drone Control | Day 5
Script: 02_waypoint_navigation.py

PURPOSE:
    Flies the drone through a list of GPS-style 3D waypoints
    defined in AirSim's NED coordinate system.

COORDINATE SYSTEM REMINDER:
    X = North (forward),  Y = East (right),  Z = Down (use NEGATIVE for altitude)
    All distances in METERS from the drone's starting position.

HOW TO RUN:
    1. Make sure 01_basic_flight.py already works
    2. Unreal Engine + AirSim must be running
    3. python 02_waypoint_navigation.py
"""

import airsim
import time
import math


# ─────────────────────────────────────────────
#  WAYPOINT DEFINITION
# ─────────────────────────────────────────────
# Each waypoint: (x, y, z, label)
# z is NEGATIVE for altitude (NED system)
# Example: (10, 0, -5, "WP1") → 10m north, same east, 5m altitude

WAYPOINTS = [
    (  0,   0, -5,  "Launch Pad Hover"),    # Arm and climb to 5m
    ( 10,   0, -5,  "Alpha"),               # 10m North
    ( 10,  10, -8,  "Bravo"),               # 10m North, 10m East, climb to 8m
    (  0,  10, -8,  "Charlie"),             # Back south, still 10m East
    (  0,   0, -5,  "Return Home"),         # RTH - back to start at 5m
]

# Flight parameters
CRUISE_SPEED    = 3.0    # m/s between waypoints
WAYPOINT_RADIUS = 1.5    # meters — how close counts as "reached"
HOVER_AT_WP     = 2.0    # seconds to hover at each waypoint


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def connect():
    print("[INFO] Connecting to AirSim ...")
    client = airsim.MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    print("[OK]   Connected!")
    return client


def get_position(client):
    """Return current (x, y, z) position tuple."""
    pos = client.getMultirotorState().kinematics_estimated.position
    return pos.x_val, pos.y_val, pos.z_val


def distance_to(client, tx, ty, tz):
    """Euclidean distance from drone's current position to a target."""
    cx, cy, cz = get_position(client)
    return math.sqrt((tx - cx)**2 + (ty - cy)**2 + (tz - cz)**2)


def fly_to_waypoint(client, x, y, z, label, speed=CRUISE_SPEED):
    """
    Command the drone to fly to a specific 3D point.

    Args:
        x, y, z  : Target position in NED meters
        label    : Human-readable name for logging
        speed    : Cruise speed in m/s
    """
    print(f"\n[→] Flying to waypoint [{label}]  X:{x}  Y:{y}  Z:{z}  ({-z:.1f}m alt)")
    client.moveToPositionAsync(
        x=x, y=y, z=z,
        velocity=speed,
        timeout_sec=60,             # Safety timeout
        drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom,
        yaw_mode=airsim.YawMode(is_rate=False, yaw_or_rate=0)
        # yaw_or_rate=0 keeps the nose pointing North
        # Change to: yaw_or_rate=90  to face East while flying
    ).join()

    # Confirm arrival
    dist = distance_to(client, x, y, z)
    print(f"[OK]   Reached [{label}]  (error: {dist:.2f}m)  Hovering {HOVER_AT_WP}s ...")
    client.hoverAsync().join()
    time.sleep(HOVER_AT_WP)


def print_flight_status(client, wp_index, total_wps):
    """Show a quick status line during flight."""
    cx, cy, cz = get_position(client)
    print(f"       Status: WP {wp_index}/{total_wps}  "
          f"Pos({cx:.1f}, {cy:.1f}, {cz:.1f})  Alt≈{-cz:.1f}m")


# ─────────────────────────────────────────────
#  MAIN MISSION
# ─────────────────────────────────────────────
def run_waypoint_mission(client):
    """Execute the full waypoint flight plan."""

    print("\n" + "="*55)
    print(f"  WAYPOINT MISSION — {len(WAYPOINTS)} waypoints")
    print("="*55)

    # ── Takeoff first ──
    print("[INFO] Takeoff sequence ...")
    client.takeoffAsync().join()
    time.sleep(1)

    total = len(WAYPOINTS)
    for i, (x, y, z, label) in enumerate(WAYPOINTS, start=1):
        print_flight_status(client, i, total)
        fly_to_waypoint(client, x, y, z, label)

    # ── Mission complete ──
    print("\n[INFO] All waypoints reached — landing ...")
    client.landAsync().join()
    client.armDisarm(False)
    client.enableApiControl(False)
    print("[OK]   Mission complete. Drone disarmed.")


# ─────────────────────────────────────────────
#  ADVANCED: Fly a SQUARE pattern automatically
# ─────────────────────────────────────────────
def fly_square(client, side_m=10, altitude_m=5, speed=2.5):
    """
    Automatically generate and fly a square pattern.

    Args:
        side_m      : Length of each side in meters
        altitude_m  : Constant flight altitude
        speed       : Cruise speed
    """
    z = -altitude_m     # NED: negative = up

    square_waypoints = [
        (side_m,      0,      z, "NE Corner"),
        (side_m,  side_m,     z, "SE Corner"),
        (0,       side_m,     z, "SW Corner"),
        (0,           0,      z, "Home"),
    ]

    print("\n[INFO] Flying SQUARE pattern "
          f"({side_m}m sides at {altitude_m}m altitude) ...")
    client.takeoffAsync().join()
    client.moveToZAsync(z, velocity=2).join()
    time.sleep(1)

    for x, y, zz, label in square_waypoints:
        fly_to_waypoint(client, x, y, zz, label, speed)

    client.landAsync().join()
    client.armDisarm(False)
    client.enableApiControl(False)
    print("[OK]   Square flight done.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    client = connect()

    try:
        # Change to fly_square(client) to run the square pattern instead
        run_waypoint_mission(client)

    except KeyboardInterrupt:
        print("\n[WARN] Interrupted — emergency landing ...")
        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
