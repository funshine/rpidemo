#!/usr/bin/env python

import socket
import threading
import time


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

        self.socket.send("\nWelcome to the server\n\n")

        data = "dummydata"

        try:
            while len(data) and self.running:
                data = self.socket.recv(2048)
                print("Receive from client " + self.ip + ":" + str(self.port) + " : " + data)
                # self.socket.send("You sent me : " + data)
        except socket.error as msg:
            print("ClientReceiveThread Socket Error: %s" % msg)
        except TypeError as msg:
            print("ClientReceiveThread Type Error: %s" % msg)
        finally:
            self.socket.close()
        print("Client disconnected...")


class ClientSendThread(threading.Thread):

    def __init__(self, ip, port, socket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.socket = socket
        self.sendcount = 0
        self.running = False
        print("[+] New Send thread started for " + ip + ":" + str(port))

    def run(self):
        # print("Connection from : " + ip + ":" + str(port))

        self.socket.send("\nWelcome to the server\n\n")
        self.running = True

        try:
            while self.running:
                data = "This is from server message number: " + str(self.sendcount)
                self.sendcount += 1
                print("Send to client " + self.ip + ":" + str(self.port) + " : " + data)
                self.socket.send(data)
                time.sleep(2)
        except socket.error as msg:
            print("ClientSendThread Socket Error: %s" % msg)
        except TypeError as msg:
            print("ClientSendThread Type Error: %s" % msg)
        finally:
            self.socket.close()


class ClientThread():
    def __init__(self, ip, port, socket):
        self.sendthread = ClientSendThread(ip, port, socket)
        self.receivethread = ClientReceiveThread(ip, port, socket)
        self.socket = socket

    def start(self):
        self.sendthread.start()
        self.receivethread.start()


host = "0.0.0.0"
port = 9898

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host, port))
threads = []

while True:
    try:
        tcpsock.listen(4)
        print("\nListening for incoming connections...")
        (clientsock, (ip, port)) = tcpsock.accept()
        newthread = ClientThread(ip, port, clientsock)
        newthread.start()
        threads.append(newthread)
    except KeyboardInterrupt:
        print("User abort!")
        for t in threads:
            t.socket.close()
            t.sendthread.running = False
            t.receivethread.running = False
        break

for t in threads:
    t.sendthread.join()
    t.receivethread.join()
