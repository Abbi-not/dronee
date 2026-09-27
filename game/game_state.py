from enum import Enum, auto


class State(Enum):
    FLYING = auto()
    CRASHED = auto()
    FINISHED = auto()


class GameState:
    """Tracks which checkpoint is next and whether the flight is still
    live. Kept independent of Ursina so it's easy to reason about or test
    on its own: Start -> Flying -> Checkpoint 1..N -> Finished / Crashed."""

    def __init__(self, total_checkpoints):
        self.total_checkpoints = total_checkpoints
        self.checkpoints_passed = 0
        self.state = State.FLYING

    def next_checkpoint(self):
        """Index of the checkpoint the drone must hit next, or None if
        all checkpoints are already cleared."""
        if self.checkpoints_passed < self.total_checkpoints:
            return self.checkpoints_passed
        return None

    def pass_checkpoint(self):
        self.checkpoints_passed += 1

    def all_checkpoints_passed(self):
        return self.checkpoints_passed >= self.total_checkpoints

    def crash(self):
        self.state = State.CRASHED

    def finish(self):
        self.state = State.FINISHED

    def reset(self):
        self.checkpoints_passed = 0
        self.state = State.FLYING
