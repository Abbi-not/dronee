from ursina import Entity, Sky, DirectionalLight, color, Vec3


def build_environment():
    """Ground plane, sky, and a directional light. Nothing fancier is
    needed for the MVP -- the obstacles and checkpoints do the work of
    making the space read as a course rather than an empty void."""
    Entity(
        model="plane",
        scale=(120, 1, 120),
        color=color.rgb(70, 110, 60),
        texture="white_cube",
        texture_scale=(60, 60),
        collider="box",
    )
    Sky()
    light = DirectionalLight()
    light.look_at(Vec3(1, -2, -1))
