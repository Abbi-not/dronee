# Drone Flight Sim — MVP

> Fly a drone through a small 3D obstacle course and reach checkpoints without crashing.

Built in Python with [Ursina](https://www.ursinaengine.org/) (a thin, beginner-friendly
wrapper around Panda3D). No multiplayer, no realistic aerodynamics, no AI — just
position, velocity, rotation, collision, and game state, which is exactly what the
follow-up UDP-controlled version will need.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

> Note: this was written directly against Ursina's documented API but hasn't been
> run in a live Python environment on this end (no display / package install
> available here), so budget a few minutes for first-run troubleshooting —
> most likely a version-specific `Text`/`Entity` keyword argument if you're on
> a very different Ursina release than the one pinned in `requirements.txt`.

## Controls

| Key | Action |
|---|---|
| `W` / `S` | Forward / backward |
| `A` / `D` | Strafe left / right |
| `Q` / `E` | Yaw left / right |
| `Space` | Ascend |
| `Shift` | Descend |
| hold right mouse + drag | Look around |
| `R` | Restart |
| `Esc` | Quit |

## Objective

```
Start
  ↓
◯ Checkpoint 1
  ↓
◯ Checkpoint 2
  ↓
◯ Checkpoint 3
  ↓
🏁 Finish
```

Hit an obstacle at any point and it's a crash — press `R` to restart. Checkpoints
must be cleared in order; flying through the wrong one does nothing.

## Project structure

```
drone-simulator/
├── main.py                  # wires everything together, owns the Ursina update() loop
├── drone/
│   ├── drone.py              # the Drone entity: position, velocity, yaw, model
│   ├── movement.py           # pure functions: input -> acceleration -> velocity
│   └── camera.py             # simple third-person chase camera
├── world/
│   ├── environment.py        # ground, sky, lighting
│   ├── obstacle.py           # obstacle entities + AABB data
│   └── checkpoint.py         # checkpoint/finish rings (built from cubes, no assets needed)
├── game/
│   ├── game_state.py         # Flying / Crashed / Finished state machine
│   ├── collision.py          # drone <-> obstacle / drone <-> checkpoint checks
│   └── timer.py               # flight stopwatch for the HUD and finish summary
├── networking/
│   └── udp_server.py         # Phase 6 — NOT wired into main.py yet, see below
├── scripts/
│   └── send_test_control.py  # fires test UDP messages at udp_server.py
└── config/
    └── level.json            # start position, obstacles, checkpoints, finish zone
```

## What's implemented (Phases 1–5, 7)

- **3D world**: ground, sky, a handful of box obstacles, three checkpoint rings, a finish
  zone — all positioned via `config/level.json` so you can redesign the course without
  touching code.
- **Movement**: WASD + Space/Shift, with simple acceleration → drag → velocity → position
  physics (`drone/movement.py`) instead of instant on/off movement.
- **Orientation**: Q/E yaw the drone; forward motion is relative to the drone's heading.
- **Collision**: a deliberately simple AABB check against obstacles, and a
  radius-plus-plane-distance check for checkpoints (`game/collision.py`) — no physics
  engine callbacks, just code you can read start to finish.
- **Game state**: `game/game_state.py` tracks which checkpoint is next and whether
  you're flying, crashed, or finished.
- **HUD**: speed, altitude, checkpoint count, and a flight timer, plus a finish summary
  (time / checkpoints / distance flown) and a crash message with a restart prompt.

## Tuning the feel

Everything below lives as named constants near the top of each file, so you
can nudge them without hunting through logic:

| File | Constant | Effect |
|---|---|---|
| `drone/movement.py` | `THRUST`, `VERTICAL_THRUST` | how hard the drone accelerates per input |
| `drone/movement.py` | `DRAG_ACTIVE_PER_SEC` | how much speed carries over while you're holding a direction (lower = tighter/twitchier) |
| `drone/movement.py` | `DRAG_IDLE_PER_SEC` | how fast it stops once you let go (lower = snappier stop, higher = more glide) |
| `drone/movement.py` | `VERTICAL_HOLD_STRENGTH` | how firmly altitude-hold resists vertical drift when Space/Shift aren't held |
| `drone/drone.py` | `YAW_ACCEL`, `YAW_MAX_RATE`, `YAW_DRAG_PER_SEC` | turning speed and how much it eases in/out |
| `drone/camera.py` | `follow_speed`, `look_speed` (constructor args) | camera responsiveness — higher = snappier/closer to instant, lower = smoother but laggier |

If it's still not quite right after a play test, the two most common knobs are
`DRAG_IDLE_PER_SEC` (stiff vs. floaty stopping) and camera `follow_speed`
(sluggish vs. jittery camera).

## What's next: Phase 6 — UDP control

`networking/udp_server.py` is a working UDP listener but it's **not** imported by
`main.py` yet, on purpose — get the keyboard version feeling good first. It listens for
messages like:

```
MOVE,1,0,0
CONTROL,forward=1,yaw=0.2,altitude=0
```

and stores the latest values, thread-safely, for the game loop to read. Try it standalone:

```bash
python networking/udp_server.py       # terminal 1
python scripts/send_test_control.py   # terminal 2
```

Once that's confirmed working, wiring it in is a matter of reading `server.latest()`
inside `main.py`'s `update()` and feeding those values into
`drone/movement.compute_acceleration()` alongside (or instead of) `held_keys` — the same
architecture the target job described, just with a drone instead of a robot arm.
# dronee
