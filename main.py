"""
Drone Flight Sim -- MVP
=======================
Fly a drone through a small 3D obstacle course and reach three checkpoints,
in order, then the finish zone, without crashing.

Run:
    pip install -r requirements.txt
    python main.py

Controls:
    W / S       forward / backward
    A / D       strafe left / right
    Q / E       yaw left / right
    Space       ascend
    Shift       descend
    hold right mouse + drag   look around
    R           restart
    Esc         quit
"""
import json
from pathlib import Path

from ursina import Ursina, Text, color, held_keys, time as ursina_time, application, window

from drone.drone import Drone
from drone.camera import ThirdPersonCamera
from world.environment import build_environment
from world.obstacle import build_obstacles
from world.checkpoint import build_checkpoints
from game.game_state import GameState, State
from game.collision import drone_hits_obstacle, drone_hits_checkpoint
from game.timer import FlightTimer

CONFIG_PATH = Path(__file__).parent / "config" / "level.json"


def load_level():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


app = Ursina()
window.vsync = True  # steadier frame pacing than uncapped, less camera/physics jitter

MAX_DT = 1 / 30  # clamp so a lag spike can't cause a big physics jump or a missed collision

level = load_level()

build_environment()

drone = Drone(start_position=level["start_position"])
cam = ThirdPersonCamera(target=drone)

obstacles = build_obstacles(level["obstacles"])
checkpoints = build_checkpoints(level["checkpoints"])
finish_zone = build_checkpoints([level["finish"]], is_finish=True)[0]

game_state = GameState(total_checkpoints=len(checkpoints))
timer = FlightTimer()

hud = Text(
    text="",
    position=(-0.86, 0.46),
    scale=1.4,
    color=color.azure,
)
message = Text(
    text="",
    origin=(0, 0),
    position=(0, 0.15),
    scale=2.5,
    color=color.red,
)

timer.start()


def reset_level():
    drone.reset(level["start_position"])
    for cp in checkpoints:
        cp.reset()
    finish_zone.reset()
    game_state.reset()
    timer.reset()
    timer.start()
    message.text = ""


def update():
    cam.update()

    if game_state.state != State.FLYING:
        return

    dt = min(ursina_time.dt, MAX_DT)
    drone.handle_input(held_keys, dt)
    drone.update_physics(dt)

    for obstacle in obstacles:
        if drone_hits_obstacle(drone, obstacle):
            game_state.crash()
            timer.stop()
            message.color = color.red
            message.text = "CRASHED\n\nPress R to restart"
            return

    next_index = game_state.next_checkpoint()
    if next_index is not None:
        cp_entity = checkpoints[next_index]
        if drone_hits_checkpoint(drone, cp_entity):
            cp_entity.mark_passed()
            game_state.pass_checkpoint()

    if game_state.all_checkpoints_passed() and drone_hits_checkpoint(drone, finish_zone):
        timer.stop()
        game_state.finish()
        message.color = color.green
        message.text = (
            "FLIGHT COMPLETE\n\n"
            f"Time: {timer.formatted()}\n"
            f"Checkpoints: {game_state.checkpoints_passed}/{game_state.total_checkpoints}\n"
            f"Distance: {drone.distance_travelled:.0f}m"
        )

    hud.text = (
        f"Speed: {drone.speed():.1f} m/s\n"
        f"Altitude: {drone.entity.y:.1f} m\n"
        f"Checkpoints: {game_state.checkpoints_passed}/{game_state.total_checkpoints}\n"
        f"Time: {timer.formatted()}"
    )


def input(key):
    if key == "r":
        reset_level()
    if key == "escape":
        application.quit()


app.run()
