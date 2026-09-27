"""
Deliberately simple collision checks: axis-aligned box overlap for
obstacles, and a radius + plane-distance check for checkpoints. No
physics-engine collision callbacks -- this is meant to be read and
understood, per the MVP's "just detect drone <-> obstacle" scope.
"""


def drone_hits_obstacle(drone, obstacle):
    p = drone.position
    o = obstacle.position
    h = obstacle.half_extents
    r = drone.RADIUS
    return (
        abs(p.x - o.x) < h.x + r
        and abs(p.y - o.y) < h.y + r
        and abs(p.z - o.z) < h.z + r
    )


def drone_hits_checkpoint(drone, checkpoint, plane_tolerance=1.2):
    p = drone.position
    c = checkpoint.position
    dx, dy, dz = p.x - c.x, p.y - c.y, p.z - c.z
    radial = (dx ** 2 + dy ** 2) ** 0.5
    return radial < checkpoint.radius and abs(dz) < plane_tolerance
