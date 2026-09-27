import time as pytime


class FlightTimer:
    """A plain wall-clock stopwatch, independent of Ursina's frame timing
    so pausing/resuming the game loop doesn't need to touch this class."""

    def __init__(self):
        self._start = None
        self._stop = None

    def start(self):
        self._start = pytime.time()
        self._stop = None

    def stop(self):
        if self._stop is None:
            self._stop = pytime.time()

    def reset(self):
        self._start = None
        self._stop = None

    def elapsed(self):
        if self._start is None:
            return 0.0
        end = self._stop if self._stop is not None else pytime.time()
        return end - self._start

    def formatted(self):
        total = self.elapsed()
        minutes = int(total // 60)
        seconds = int(total % 60)
        return f"{minutes:02d}:{seconds:02d}"
