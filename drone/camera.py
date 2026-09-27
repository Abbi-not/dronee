import math

from ursina import camera, mouse, Vec3, time as ursina_time


def _lerp_vec3(a, b, t):
    return Vec3(
        a.x + (b.x - a.x) * t,
        a.y + (b.y - a.y) * t,
        a.z + (b.z - a.z) * t,
    )


class ThirdPersonCamera:
    """
    Stays behind and above the drone based on the drone's yaw. Holding the
    right mouse button and dragging adds a look-around offset without
    changing the drone's actual heading -- deliberately not a "complicated
    camera system", per the MVP scope.

    Position and look-target are both lerped toward their desired values
    each frame (instead of being set directly) so the camera glides rather
    than snapping/jittering as the drone accelerates or turns. Raise
    follow_speed / look_speed for a snappier camera, lower them for a
    lazier, more cinematic one.
    """

    def __init__(self, target, distance=8.0, height=3.5, follow_speed=6.0, look_speed=9.0):
        self.target = target
        self.distance = distance
        self.height = height
        self.yaw_offset = 0.0
        self.follow_speed = follow_speed
        self.look_speed = look_speed
        self._look_target = target.position

        # snap the camera to its starting spot immediately so it doesn't
        # glide in from the world origin on the first frame
        self._snap_to_target()

    def _desired_position(self):
        yaw = math.radians(self.target.yaw + 180 + self.yaw_offset)
        pos = self.target.position
        return Vec3(
            pos.x + math.sin(yaw) * self.distance,
            pos.y + self.height,
            pos.z + math.cos(yaw) * self.distance,
        )

    def _snap_to_target(self):
        camera.position = self._desired_position()
        self._look_target = self.target.position + Vec3(0, 0.5, 0)
        camera.look_at(self._look_target)

    def update(self):
        # damp the raw mouse delta a little so a fast flick doesn't yank
        # the view; mouse.velocity is already per-frame so this stays
        # framerate-reasonable for typical frame times
        if mouse.right:
            self.yaw_offset -= mouse.velocity[0] * 160

        dt = ursina_time.dt
        desired = self._desired_position()
        follow_t = min(1, self.follow_speed * dt)
        camera.position = _lerp_vec3(camera.position, desired, follow_t)

        look_t = min(1, self.look_speed * dt)
        target_look = self.target.position + Vec3(0, 0.5, 0)
        self._look_target = _lerp_vec3(self._look_target, target_look, look_t)
        camera.look_at(self._look_target)
