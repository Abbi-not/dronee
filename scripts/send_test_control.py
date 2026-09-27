"""
Fires a few test control messages at the UDP server (networking/udp_server.py)
so you can confirm it's receiving before wiring it into the game loop.

Usage:
    python networking/udp_server.py      # in one terminal
    python scripts/send_test_control.py  # in another
"""
import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ("127.0.0.1", 5555)

messages = [
    "MOVE,1,0,0",
    "MOVE,0,1,0",
    "CONTROL,forward=0.5,yaw=0.3,altitude=1",
    "MOVE,0,0,0",
]

for msg in messages:
    sock.sendto(msg.encode("utf-8"), addr)
    print("sent:", msg)
    time.sleep(1)
