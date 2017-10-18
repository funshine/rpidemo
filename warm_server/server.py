#!/usr/bin/env python

import socket
import threading
import time, struct
import select
import crc

def fmt2hex(str):
    if str is not None:
        return ':'.join(x.encode('hex') for x in str)  # python 2
        # return ':'.join(hex(x) for x in str) # python 3
    return None

class ClientReceiveThread(threading.Thread):

    def __init__(self, ip, port, socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.running = False
        print("[+] New Receive thread started for " + ip + ":" + str(port))

    def run(self):
        print("Connection from : " + ip + ":" + str(port))
        self.running = True

        # self.socket.send("\nWelcome to the server\n\n")

        data = "dummydata"

        try:
            while len(data) and self.running:
                data = self.socket.recv(2048)
                print("Receive from client " + self.ip + ":" + str(self.port) + " : " + fmt2hex(data))
                # readable, writable, expt = select.select([self.socket], [], [], 5)
                # for r in readable:
                #     data = r.recv(2048)
                #     print("Receive from client " + self.ip + ":" + str(self.port) + " : " + data)

        except socket.error as msg:
            print("ClientReceiveThread Socket Error: %s" % msg)
        finally:
            self.socket.close()
        print("Client disconnected...")


class ClientSendThread(threading.Thread):

    def __init__(self, ip, port, socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.running = False
        self.data = []
        print("[+] New Send thread started for " + ip + ":" + str(port))

    def run(self):
        # print("Connection from : " + ip + ":" + str(port))

        self.socket.send("\nWelcome to the server\n\n")
        self.running = True

        try:
            while self.running:
                time.sleep(5)
                if len(self.data) == 0:
                    self.data.append(get_command(1, 0, 0, 1))
                for d in self.data:
                    print("Send to client " + self.ip + ":" + str(self.port) + " : " + fmt2hex(d))
                    nsent = self.socket.send(d)
                self.data = []
                
        except socket.error as msg:
            print("ClientSendThread Socket Error: %s" % msg)
        finally:
            self.socket.close()

    def queue(self, data):
        self.data.append(data)

class InputThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False

    def run(self):
        self.running = True
        func = 0x01
        val = 0
        while self.running:
            vals = raw_input('Enter key, value(temperature/on/off), seperate with space: ').split()
            print(vals)
            if len(vals)<2:
                print("Must provide key and value")
                continue
            try:
                key = int(vals[0])
                print(key)
            except ValueError as ve:
                print('Key must be numbers')
                print(ve)
                continue

            if vals[1].upper() == 'ON':
                func = 0x02
                val = 1
                print(vals[1])
            elif vals[1].upper() == 'OFF':
                func = 0x02
                val = 0
                print(vals[1])
            else:
                try:
                    temp = int(vals[1])
                    func = 0x04
                    val = temp
                    print(temp)
                except ValueError as ve:
                    print('Values must be temperature or "on"/"off"')
                    print(ve)
                    continue
            data = get_command(1, key, val, func)
            for t in sendthreads:
                t.queue(data)

class ClientThread():
    def __init__(self, ip, port, socket):
        self.sendthread = ClientSendThread(ip, port, socket)
        self.receivethread = ClientReceiveThread(ip, port, socket)
        self.socket = socket

    def start(self):
        self.sendthread.start()
        self.receivethread.start()

def get_command(addr, dev, val, func):
    # construct the bit-stream of an instruction
    if func == 0x01:
        PLUS = 0
    else:
        PLUS = 7 << 5
    cmd = struct.pack('6B', PLUS + addr, 0x06, dev, 0x04, func, val)
    _crc = crc.calc_string(cmd, crc.INITIAL_MODBUS)
    _crc = ((_crc & 0XFF) << 8) + ((_crc & 0xFF00) >> 8)
    return cmd + struct.pack('H', _crc)

host = "0.0.0.0"
port = 9898

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host, port))

recvthreads = []
sendthreads = []

cmdthread = InputThread()
cmdthread.start()

while True:
    try:
        tcpsock.listen(4)
        print("\nListening for incoming connections...")
        (clientsock, (ip, port)) = tcpsock.accept()
        newclient = ClientThread(ip, port, clientsock)
        newclient.start()
        recvthreads.append(newclient.receivethread)
        sendthreads.append(newclient.sendthread)
    except KeyboardInterrupt:
        print("User abort!")
        for t in recvthreads:
            t.running = False
        for t in sendthreads:
            t.running = False
        cmdthread.running = False
        break

for t in recvthreads:
    t.join()
for t in sendthreads:
    t.join()

cmdthread.join()
