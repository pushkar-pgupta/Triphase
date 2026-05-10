"""
Person 2 - Drone Control | Day 3
Script: 01_basic_flight.py

PURPOSE:
    Connects to AirSim running inside Unreal Engine and performs
    basic drone maneuvers: arm, takeoff, hover, directional movement, land.

HOW TO RUN:
    1. Open Unreal Engine with your AirSim project
    2. Press PLAY in UE to start the simulation
    3. In a separate terminal on your PC, run:
           pip install airsim
           python 01_basic_flight.py

COORDINATE SYSTEM (AirSim uses NED - North East Down):
    X  → Forward (North)
    Y  → Right   (East)
    Z  → Down    (NEGATIVE Z = going UP)
    Yaw: degrees, clockwise from North
"""

import airsim
import time

# ─────────────────────────────────────────────
#  CONNECT TO AIRSIM
# ─────────────────────────────────────────────
def connect():
    """Connect to the AirSim simulation running in Unreal Engine."""
    print("[INFO] Connecting to AirSim (make sure UE simulation is running)...")
    client = airsim.MultirotorClient()          # Creates connection to localhost:41451
    client.confirmConnection()                  # Verifies the connection is alive
    client.enableApiControl(True)               # Hands control over to our Python script
    client.armDisarm(True)                      # Arms the drone motors
    print("[OK]   Connected and armed!")
    return client


# ─────────────────────────────────────────────
#  TAKEOFF
# ─────────────────────────────────────────────
def takeoff(client, altitude_m=3.0):
    """
    Lift the drone to a target altitude above the ground.

    Args:
        client      : AirSim MultirotorClient
        altitude_m  : How many meters to rise (default: 3 m)
    """
    print(f"[INFO] Taking off to {altitude_m} m ...")
    client.takeoffAsync().join()                # Built-in takeoff (rises ~2-3 m)

    # Move to our exact desired altitude
    # Z is negative because AirSim uses NED (Down = positive Z)
    client.moveToZAsync(-altitude_m, velocity=2).join()
    print(f"[OK]   Airborne at ~{altitude_m} m")
    time.sleep(1)


# ─────────────────────────────────────────────
#  HOVER  (stay still)
# ─────────────────────────────────────────────
def hover(client, duration_s=3.0):
    """
    Hold position in the air for a set number of seconds.

    Args:
        client      : AirSim MultirotorClient
        duration_s  : Seconds to hover (default: 3)
    """
    print(f"[INFO] Hovering for {duration_s}s ...")
    client.hoverAsync().join()                  # Tell AirSim to hold position
    time.sleep(duration_s)
    print("[OK]   Hover complete")


# ─────────────────────────────────────────────
#  DIRECTIONAL MOVEMENT
# ─────────────────────────────────────────────
def move_forward(client, distance_m=5.0, speed=2.0):
    """Move the drone forward (North / +X direction)."""
    print(f"[INFO] Moving FORWARD {distance_m} m ...")
    client.moveByVelocityAsync(
        vx=speed,   # forward velocity  (m/s)
        vy=0,       # no sideways drift
        vz=0,       # no vertical drift
        duration=distance_m / speed   # time = distance / speed
    ).join()
    hover(client, 1)


def move_backward(client, distance_m=5.0, speed=2.0):
    """Move the drone backward (South / -X direction)."""
    print(f"[INFO] Moving BACKWARD {distance_m} m ...")
    client.moveByVelocityAsync(
        vx=-speed,
        vy=0,
        vz=0,
        duration=distance_m / speed
    ).join()
    hover(client, 1)


def move_right(client, distance_m=5.0, speed=2.0):
    """Move the drone right (East / +Y direction)."""
    print(f"[INFO] Moving RIGHT {distance_m} m ...")
    client.moveByVelocityAsync(
        vx=0,
        vy=speed,   # positive Y = right/east
        vz=0,
        duration=distance_m / speed
    ).join()
    hover(client, 1)


def move_left(client, distance_m=5.0, speed=2.0):
    """Move the drone left (West / -Y direction)."""
    print(f"[INFO] Moving LEFT {distance_m} m ...")
    client.moveByVelocityAsync(
        vx=0,
        vy=-speed,  # negative Y = left/west
        vz=0,
        duration=distance_m / speed
    ).join()
    hover(client, 1)


def move_up(client, distance_m=3.0, speed=2.0):
    """Gain altitude."""
    print(f"[INFO] Moving UP {distance_m} m ...")
    # Get current Z, go more negative (higher)
    state = client.getMultirotorState()
    current_z = state.kinematics_estimated.position.z_val
    target_z = current_z - distance_m           # subtract = go up in NED
    client.moveToZAsync(target_z, velocity=speed).join()
    hover(client, 1)


def move_down(client, distance_m=2.0, speed=2.0):
    """Lose altitude (will not go below ground)."""
    print(f"[INFO] Moving DOWN {distance_m} m ...")
    state = client.getMultirotorState()
    current_z = state.kinematics_estimated.position.z_val
    target_z = current_z + distance_m           # add = go down in NED
    client.moveToZAsync(target_z, velocity=speed).join()
    hover(client, 1)


def yaw_turn(client, degrees=90, speed=30):
    """
    Rotate (yaw) the drone in place.

    Args:
        degrees  : Positive = clockwise, Negative = counter-clockwise
        speed    : Degrees per second
    """
    direction = "clockwise" if degrees > 0 else "counter-clockwise"
    print(f"[INFO] Yawing {abs(degrees)}° {direction} ...")
    client.rotateByYawRateAsync(
        yaw_rate=speed if degrees > 0 else -speed,
        duration=abs(degrees) / speed
    ).join()
    hover(client, 1)


# ─────────────────────────────────────────────
#  LAND
# ─────────────────────────────────────────────
def land(client):
    """Safely land the drone and disarm motors."""
    print("[INFO] Landing ...")
    client.landAsync().join()
    client.armDisarm(False)                     # Disarm motors after landing
    client.enableApiControl(False)              # Return control to UE
    print("[OK]   Landed and disarmed. Flight complete.")


# ─────────────────────────────────────────────
#  UTILITY: Print current position
# ─────────────────────────────────────────────
def print_position(client):
    """Print the drone's current GPS-like position in the sim."""
    state = client.getMultirotorState()
    pos = state.kinematics_estimated.position
    print(f"  → Position  X:{pos.x_val:.2f}m  Y:{pos.y_val:.2f}m  Z:{pos.z_val:.2f}m "
          f"(altitude ≈ {-pos.z_val:.2f}m AGL)")


# ─────────────────────────────────────────────
#  MAIN DEMO SEQUENCE
# ─────────────────────────────────────────────
if __name__ == "__main__":
    client = connect()

    try:
        # --- Takeoff ---
        takeoff(client, altitude_m=5)
        print_position(client)

        # --- Hover in place ---
        hover(client, duration_s=3)

        # --- Basic movement demo ---
        move_forward(client, distance_m=5)
        print_position(client)

        move_right(client, distance_m=5)
        print_position(client)

        move_backward(client, distance_m=5)
        print_position(client)

        move_left(client, distance_m=5)
        print_position(client)

        # --- Spin 90 degrees ---
        yaw_turn(client, degrees=90)

        # --- Final hover ---
        hover(client, duration_s=2)

    except KeyboardInterrupt:
        print("\n[WARN] Interrupted by user — landing now...")

    finally:
        land(client)
