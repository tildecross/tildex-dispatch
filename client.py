#!env/bin/python3

import sys
import json
import math
import time
import socket
import select
import struct
import threading

from socketIO_client import SocketIO, LoggingNamespace

# type: obj -> str
def encode(data):
    return json.dumps(data)

# type: str -> obj
def decode(data):
    return json.loads(data)

class SocketClient(threading.Thread):
    RECV_BUFFER = 4096
    RECV_MSG_LEN = 4
    
    def __init__(self, host, port, ports=None):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.connections = [0]
        self.running = True
        self.ports = ports
        
    def _bind_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try: 
            self.sock.connect((self.host, self.port))
        except Exception as e:
            return False
        else:
            self.connections.append(self.sock)
            return True
        
    def _send(self, sock, msg):
        # Append message with length of message
        msg = struct.pack(">I", len(msg)) + msg.encode("utf-8")
        sock.send(msg)
        
    def _receive(self, sock):
        data = None
        total_len = 0
        while total_len < self.RECV_MSG_LEN:
            msg_len = sock.recv(self.RECV_MSG_LEN)
            total_len = total_len + len(msg_len)
            
        # If the message has the length prefix
        if msg_len:
            data = ""
            msg_len = struct.unpack(">I", msg_len)[0]
            total_data_len = 0
            while total_data_len < msg_len:
                chunk = sock.recv(self.RECV_BUFFER)
                
                if not chunk:
                    data = None
                    break
                else:
                    data = data + chunk.decode("utf-8")
                    total_data_len = total_data_len + len(chunk)
        
        return data
    
    def _broadcast(self, msg):
        print("Client broadcasting...")
        msg = struct.pack(">I", len(msg)) + msg.encode("utf-8")
        self.sock.sendall(msg)
    
    def _run(self):
        print("Starting socket client (%s, %s)..." % (self.host, self.port))
        while self.running:
            try:
                # Timeout every 60 seconds
                selection = select.select(self.connections, [], [], 60)
                read_sock, write_sock, error_sock = selection
            except select.error:
                print("ERROR!!!")
                continue
            else:
                for sock in read_sock:
                    if sock == 0:
                        # self._send(self.sock, encode({}))
                        continue
                    elif sock == self.sock:
                        try:
                            data = self._receive(sock)
                            if data:
                                message = decode(data)
                                print("Received: %s" % message)
                                if (self.ports is not None):
                                    name = message["name"]
                                    data = message["data"]
                                    websock_ports = self.ports["websockets"]
                                    port = websock_ports["txdispatch"]
                                    websock = SocketIO("localhost", port)
                                    websock.emit("socket", message)
                                    # self.websock.emit("message", data,
                                    #     room=)
                                else:
                                    print("Error: Ports not set!")
                        except socket.error:
                            # Client is no longer replying
                            print("Disconnecting...")
                            attempts = 5
                            reconnected = False
                            while not reconnected or attempts > 0:
                                time.sleep(5)
                                print("Trying to reconnect...")
                                reconnected = self._bind_socket()
                                if not reconnected:
                                    attempts = attempts - 1
                                
                            if not reconnected:
                                self.running = False
                                break
        # Clear the socket connection
        self.stop()
    
    def run(self):
        connected = self._bind_socket()
        if connected:
            self._run()
        
    def stop(self):
        self.running = False
        self.sock.close()
