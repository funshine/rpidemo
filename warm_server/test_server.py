#!/usr/bin/python
# coding: utf-8

import socket
import sys, time

HOST, PORT = "localhost", 9898
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(data + "\n")

    # Receive data from the server and shut down
    while 1:
        received = sock.recv(1024)
        if not received: break
        print(received)
        time.sleep(0.5)
        sock.sendall(received)
finally:
    sock.close()

print("Sent:     {}".format(data))
print("Received: {}".format(received))