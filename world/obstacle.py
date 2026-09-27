from ursina import Entity, Vec3, color


class Obstacle:
    """A solid box obstacle. Position/scale come straight from level.json
    so the course can be redesigned without touching code."""

    def __init__(self, position, scale):
        self.position = Vec3(*position)
        self.half_extents = Vec3(scale[0] / 2, scale[1] / 2, scale[2] / 2)
        self.entity = Entity(
            model="cube",
            color=color.gray,
            position=self.position,
            scale=Vec3(*scale),
        )


def build_obstacles(obstacle_configs):
    return [Obstacle(o["position"], o["scale"]) for o in obstacle_configs]
