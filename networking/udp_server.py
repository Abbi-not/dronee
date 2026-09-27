"""
Phase 6 -- UDP control input.

This is NOT wired into main.py. Per the project plan, networking comes
after the keyboard-controlled MVP works end to end. When you're ready for
it, this listens for simple comma-separated control messages on a
background thread and stores the latest values so the game loop can read
them instead of (or blended with) held_keys.

Example messages a controller could send:
    MOVE,1,0,0
        -> forward=1, strafe=0, vertical=0
    CONTROL,forward=1,yaw=0.2,altitude=0
        -> arbitrary key=value pairs, all stored as floats

Wiring it into main.py later looks roughly like:

    from networking.udp_server import UdpControlServer
    server = UdpControlServer()
    server.start()

    # inside update():
    controls = server.latest()
    # feed controls into drone.movement.compute_acceleration()
    # instead of, or alongside, held_keys

Test it standalone with:
    python networking/udp_server.py
    python scripts/send_test_control.py
"""
import socket
import threading


class UdpControlServer:
    def __init__(self, host="0.0.0.0", port=5555):
        self.host = host
        self.port = port
        self._socket = None
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._latest = {"forward": 0.0, "strafe": 0.0, "vertical": 0.0, "yaw": 0.0}

    def start(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))
        self._socket.settimeout(0.5)
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._socket:
            self._socket.close()

    def latest(self):
        with self._lock:
            return dict(self._latest)

    def _listen(self):
        while self._running:
            try:
                data, _ = self._socket.recvfrom(1024)
            except socket.timeout:
                continue
            except OSError:
                break
            self._parse(data.decode("utf-8", errors="ignore").strip())

    def _parse(self, message):
        if not message:
            return
        parts = message.split(",")
        command = parts[0].upper()
        with self._lock:
            if command == "MOVE" and len(parts) >= 4:
                self._latest["forward"] = float(parts[1])
                self._latest["strafe"] = float(parts[2])
                self._latest["vertical"] = float(parts[3])
            elif command == "CONTROL":
                for pair in parts[1:]:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        try:
                            self._latest[key.strip()] = float(value)
                        except ValueError:
                            pass


if __name__ == "__main__":
    server = UdpControlServer()
    server.start()
    print(f"Listening for UDP control messages on {server.host}:{server.port} (Ctrl+C to stop)")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()
