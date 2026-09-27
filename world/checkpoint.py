import math

from ursina import Entity, Vec3, color

try:
    from ursina import combine
    HAS_COMBINE = True
except ImportError:
    HAS_COMBINE = False

RING_SEGMENTS = 14


class Checkpoint:
    """
    A floating ring the drone must fly through. Rendered as a ring of small
    cubes rather than a custom mesh, so the MVP has zero asset dependencies.
    The ring's hole faces along +Z, matching the drone's default forward
    direction (yaw = 0).

    Performance: 14 separate cube entities per ring means 14 draw calls.
    With 4 rings in the scene that's 56 draws for something that's visually
    one object, so the segments get merged into a single mesh via Ursina's
    combine() right after creation. If combine() isn't available in your
    installed Ursina version, it falls back to the individual cubes --
    slightly more draw calls, but functionally identical.
    """

    def __init__(self, position, radius=3.0, is_finish=False):
        self.position = Vec3(*position)
        self.radius = radius
        self.is_finish = is_finish
        self.passed = False
        self._active_color = color.lime if is_finish else color.yellow

        self.root = Entity(position=self.position)
        self._segments = []
        for i in range(RING_SEGMENTS):
            angle = (i / RING_SEGMENTS) * math.tau
            segment = Entity(
                parent=self.root,
                model="cube",
                color=self._active_color,
                scale=(0.4, 0.4, 0.4),
                position=(math.cos(angle) * radius, math.sin(angle) * radius, 0),
            )
            self._segments.append(segment)

        self._combined = None
        if HAS_COMBINE:
            try:
                merged_mesh = combine(self._segments)
                self._combined = Entity(parent=self.root, model=merged_mesh, color=self._active_color)
                for segment in self._segments:
                    segment.enabled = False
            except Exception:
                self._combined = None  # fall back to the individual cubes below

    def mark_passed(self):
        self.passed = True
        self._set_color(color.gray)

    def reset(self):
        self.passed = False
        self._set_color(self._active_color)

    def _set_color(self, c):
        if self._combined:
            self._combined.color = c
        else:
            for segment in self._segments:
                segment.color = c


def build_checkpoints(checkpoint_configs, is_finish=False):
    return [
        Checkpoint(c["position"], c.get("radius", 3.0), is_finish=is_finish)
        for c in checkpoint_configs
    ]
