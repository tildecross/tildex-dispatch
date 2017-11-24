#!env/bin/python3

import sys
import json
import socket
import select
from time import time
from flask import Flask, request
from flask_socketio import SocketIO, send, emit

import config
from client import SocketClient

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
socketio = SocketIO(app)

http_ports = config.SERVICES["http"]
sock_ports = config.SERVICES["sockets"]
websock_ports = config.SERVICES["websockets"]

app.config["SOCK"] = SocketClient("127.0.0.1", sock_ports["txdispatch"],
                        ports=config.SERVICES)

# type: obj -> str
def encode(data):
    return json.dumps(data)

# type: str -> obj
def decode(data):
    return json.loads(data)

@socketio.on("message")
def handle_message(message):
    print("Message: [%s]> %s" % (time(), message))

@socketio.on("json")
def handle_json(json):
    print("JSON: [%s]> %s" % (time(), encode(json)))

@socketio.on("socket")
def handle_socket(socket):
    print("Socket: [%s]> %s" % (time(), encode(socket)))
    name = socket.get("name", None)
    data = socket.get("data", None)
    owner = socket.get("owner", None)
    
    if owner is not None:
        emit("message", data, room=owner)

@socketio.on("connected")
def handle_connected(hello):
    print("Connected: [%s]> %s" % (time(), encode(hello)))
    json = {
        "data": "Welcome to TxDispatch!"
    }
    emit("connected", json)

@socketio.on("request")
def handle_request(req):
    print("Request: [%s]> %s" % (time(), encode(req)))
    name = req.get("name", None)
    data = req.get("data", None)
    
    if name is not None and data is not None:
        if name in list(websock_ports.keys()):
            ns = "/%s" % name
            dispatch = {
                "name": name,
                "data": data
            }
            dispatch["owner"] = request.sid
            handle_service_request(dispatch, namespace="/%s" % name)
        else:
            err = {
                "name": "error",
                "data": {
                    "code": "0x0002",
                    "message": "Service does not exist"
                }
            }
            emit("error", err)
    else:
        err = {
            "name": "error",
            "data": {
                "code": "0x0001",
                "message": "Missing name or data"
            }
        }
        emit("error", err)

def handle_service_connected(hello, namespace=None):
    if namespace is None:
        ns = request.namespace
    else:
        ns = namespace
    print("SConnected: %s@[%s]> %s" % (ns[1:], time(), str(hello)))
    json = {
        "data": "Welcome to %s!" % ns[1:]
    }
    emit("connected", json, namespace=ns)
    
def handle_service_request(req, namespace=None):
    if namespace is None:
        ns = request.namespace
    else:
        ns = namespace
    print("SRequest: %s@[%s]> %s" % (ns[1:], time(), encode(req)))
    name = req.get("name", None)
    data = req.get("data", None)
    sock = app.config["SOCK"]
    
    if name is not None and data is not None:
        sock._broadcast(encode(req))
        # pass
        # emit("request", dispatch, namespace=ns)
    else:
        err = {
            "name": "error",
            "data": {
                "code": "0x0001",
                "message": "Missing name or data"
            }
        }
        emit("error", err)

def handle_service_message(message, namespace=None):
    if namespace is None:
        ns = request.namespace
    else:
        ns = namespace
    print("SMessage: %s@[%s]> %s" % (ns[1:], time(), encode(message)))
    name = message.get("name", None)
    data = message.get("data", None)
    
    if name is not None and data is not None:
        if "owner" in data:
            owner = data["owner"]
            del data["owner"]
            emit("message", data, room=owner)
    else:
        err = {
            "name": "error",
            "data": {
                "code": "0x0002",
                "message": "Missing name or data"
            }
        }
        emit("error", err)
    
for service, port in websock_ports.items():
    ns = "/%s" % service
    socketio.on_event("connected", handle_service_connected, namespace=ns)
    socketio.on_event("request", handle_service_request, namespace=ns)
    socketio.on_event("message", handle_service_message, namespace=ns)

if __name__ == "__main__":
    app.config["SOCK"].start()
    socketio.run(app, host="localhost", port=websock_ports["txdispatch"])
    #, debug=True)
