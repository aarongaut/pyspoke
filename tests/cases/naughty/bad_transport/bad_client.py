import os
import socket

host = "127.0.0.1"
port = int(os.getenv("SPOKEPORT", 7181))


def send(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.send(data)


send(b'{"head": {"channel": "begin"}}\x00')
for __ in range(1000):
    send(b"junk")
send(b'{"head": {"channel": "end"}}\x00')
