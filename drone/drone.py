import math

from ursina import Entity, Vec3, color

from .movement import compute_acceleration, integrate, lerp_angle

YAW_ACCEL = 260.0        # deg/s^2 while Q/E is held
YAW_MAX_RATE = 110.0     # deg/s cap
YAW_DRAG_PER_SEC = 0.05  # fraction of yaw_rate kept after 1s once you release Q/E

TILT_SMOOTHING = 8.0     # higher = tilt reacts faster to velocity changes
MAX_TILT_DEGREES = 18.0


class Drone:
    """
    Wraps the Ursina entity for the drone and owns its flight state.

    Deliberately simple physics for the MVP: acceleration from input ->
    drag -> velocity -> position, rather than a full aerodynamic model.
    Yaw has its own momentum (accelerate/drag) so turning eases in and out
    instead of snapping to a fixed rate. Pitch/roll are purely cosmetic --
    they follow velocity so the drone visibly banks into motion, but they
    don't feed back into the physics.
    """

    RADIUS = 0.9  # used for collision checks

    def __init__(self, start_position):
        self.entity = Entity(
            model="cube",
            color=color.orange,
            scale=(1.2, 0.35, 1.2),
            position=Vec3(*start_position),
        )
        # four small feet so it silhouettes as a drone, not a floating crate
        for dx, dz in [(0.6, 0.6), (-0.6, 0.6), (0.6, -0.6), (-0.6, -0.6)]:
            Entity(
                parent=self.entity,
                model="cube",
                color=color.dark_gray,
                scale=(0.5, 0.08, 0.5),
                position=(dx, 0.05, dz),
            )

        self.velocity = Vec3(0, 0, 0)
        self.yaw = 0.0
        self.yaw_rate = 0.0
        self.distance_travelled = 0.0
        self._held_keys = {}

    def reset(self, start_position):
        self.entity.position = Vec3(*start_position)
        self.entity.rotation = Vec3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        self.yaw = 0.0
        self.yaw_rate = 0.0
        self.distance_travelled = 0.0

    def handle_input(self, held_keys, dt):
        """Read input for this frame. Yaw (Q/E) has its own momentum so it
        eases in and out rather than snapping to a fixed turn rate; thrust
        is applied in update_physics so it can also be driven by something
        other than the keyboard later (e.g. the UDP controller)."""
        self._held_keys = held_keys

        turning = False
        if held_keys.get("q"):
            self.yaw_rate += YAW_ACCEL * dt
            turning = True
        if held_keys.get("e"):
            self.yaw_rate -= YAW_ACCEL * dt
            turning = True

        self.yaw_rate = max(-YAW_MAX_RATE, min(YAW_MAX_RATE, self.yaw_rate))
        if not turning:
            self.yaw_rate *= YAW_DRAG_PER_SEC ** dt

        self.yaw += self.yaw_rate * dt
        self.entity.rotation_y = self.yaw

    def update_physics(self, dt):
        accel, horizontal_input = compute_acceleration(self._held_keys, self.yaw, self.velocity)
        self.velocity = integrate(self.velocity, accel, dt, horizontal_input)
        self.entity.position += self.velocity * dt
        self.distance_travelled += self.velocity.length() * dt

        # simple floor clamp so a downward-drifting drone doesn't sink
        # through the ground plane
        if self.entity.y < self.RADIUS:
            self.entity.y = self.RADIUS
            if self.velocity.y < 0:
                self.velocity.y = 0

        self._update_tilt(dt)

    def _update_tilt(self, dt):
        """Purely cosmetic bank/pitch so movement reads as flight rather
        than a box sliding on ice. Does not affect collision or physics."""
        yaw = math.radians(self.yaw)
        forward = Vec3(math.sin(yaw), 0, math.cos(yaw))
        right = Vec3(math.sin(yaw + math.pi / 2), 0, math.cos(yaw + math.pi / 2))

        target_pitch = max(-MAX_TILT_DEGREES, min(MAX_TILT_DEGREES, self.velocity.dot(forward) * 1.1))
        target_roll = max(-MAX_TILT_DEGREES, min(MAX_TILT_DEGREES,
                           -self.velocity.dot(right) * 1.1 - self.yaw_rate * 0.08))

        t = min(1, TILT_SMOOTHING * dt)
        self.entity.rotation_x = lerp_angle(self.entity.rotation_x, target_pitch, t)
        self.entity.rotation_z = lerp_angle(self.entity.rotation_z, target_roll, t)

    def speed(self):
        return self.velocity.length()

    @property
    def position(self):
        return self.entity.position
