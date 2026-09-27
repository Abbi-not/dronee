"""
Pure functions for turning key input into acceleration, and integrating
acceleration into velocity over a timestep. Kept separate from the Entity
/ rendering code (drone.py) so the flight model itself can be read, tuned,
or unit-tested on its own -- this is the "position / velocity / rotation"
core the MVP is built around.

Tuning notes (edit the constants below to change feel):
- Drag is applied as `factor ** dt` rather than a flat per-frame multiply,
  so it behaves the same at 30fps or 300fps instead of drifting depending
  on frame rate.
- Two drag rates (active vs idle) instead of one: light drag while you're
  holding a direction lets speed build up responsively; strong drag once
  you let go stops the drift/"floaty" feeling without making the controls
  feel stiff while you're actively flying.
- Vertical motion gets a simple altitude-hold: when you're not tapping
  Space/Shift, any residual vertical velocity (from gravity or momentum)
  gets cancelled out instead of the drone slowly sinking.
"""
import math

from ursina import Vec3

THRUST = 18.0             # forward/back/strafe acceleration, units/s^2
VERTICAL_THRUST = 14.0    # up/down acceleration, units/s^2
GRAVITY = 4.0             # constant downward pull before altitude-hold cancels it

DRAG_ACTIVE_PER_SEC = 0.55    # fraction of velocity kept after 1s while thrusting
DRAG_IDLE_PER_SEC = 0.06      # fraction of velocity kept after 1s once you release input
VERTICAL_HOLD_STRENGTH = 6.0  # how hard altitude-hold fights vertical drift


def compute_acceleration(held_keys, yaw_degrees, current_velocity):
    """
    held_keys: a dict-like of currently-held key names to truthy values
                (ursina's held_keys works directly; a plain dict works for tests)
    yaw_degrees: the drone's current yaw, in degrees. 0 degrees faces +Z.
    current_velocity: the drone's velocity this frame, needed for altitude-hold.

    Returns (acceleration: Vec3, horizontal_input: bool). horizontal_input
    tells the caller whether to use the "active" or "idle" drag rate.
    """
    yaw = math.radians(yaw_degrees)
    forward = Vec3(math.sin(yaw), 0, math.cos(yaw))
    right = Vec3(math.sin(yaw + math.pi / 2), 0, math.cos(yaw + math.pi / 2))

    accel = Vec3(0, 0, 0)
    horizontal_input = False
    vertical_input = False

    if held_keys.get("w"):
        accel += forward * THRUST
        horizontal_input = True
    if held_keys.get("s"):
        accel -= forward * THRUST
        horizontal_input = True
    if held_keys.get("d"):
        accel += right * THRUST
        horizontal_input = True
    if held_keys.get("a"):
        accel -= right * THRUST
        horizontal_input = True

    if held_keys.get("space"):
        accel += Vec3(0, VERTICAL_THRUST, 0)
        vertical_input = True
    if held_keys.get("shift"):
        accel -= Vec3(0, VERTICAL_THRUST, 0)
        vertical_input = True

    accel -= Vec3(0, GRAVITY, 0)

    if not vertical_input:
        accel = Vec3(accel.x, accel.y - current_velocity.y * VERTICAL_HOLD_STRENGTH, accel.z)

    return accel, horizontal_input


def integrate(velocity, acceleration, dt, horizontal_input):
    """velocity -> velocity + acceleration * dt, then framerate-independent drag."""
    velocity = velocity + acceleration * dt
    drag_per_sec = DRAG_ACTIVE_PER_SEC if horizontal_input else DRAG_IDLE_PER_SEC
    velocity = velocity * (drag_per_sec ** dt)
    return velocity


def lerp_angle(current, target, t):
    """Simple linear lerp for the small cosmetic bank/pitch angles used in
    drone.py. No wraparound handling needed since those angles stay well
    within +-20 degrees."""
    return current + (target - current) * t
