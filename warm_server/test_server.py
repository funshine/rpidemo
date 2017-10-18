#!/usr/bin/python
# coding: utf-8

import socket
import sys, time
import select

def fmt2hex(str):
    if str is not None:
        return ':'.join(x.encode('hex') for x in str)  # python 2
        # return ':'.join(hex(x) for x in str) # python 3
    return None

HOST, PORT = "localhost", 9898

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    # sock.setblocking(0)
    sock.sendall(data + "\n")
    received = None

    # Receive data from the server and shut down
    while 1:
        r, w, e = select.select([sock], [], [], 10)
        for x in r:
            x.settimeout(5.0)
            received = x.recv(1024)
            if not received: break
            x.sendall(received)
            print(fmt2hex(received))
        for x in w:
            if received is not None:
                x.sendall(received)
            received = None
        for x in e:
            print("exception in select")
            break
        time.sleep(1)
        
finally:
    sock.close()
