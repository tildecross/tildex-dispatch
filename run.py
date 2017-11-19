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

services = config.SERVICES["websockets"]

sock_ports = config.SERVICES["sockets"]
app.config["SOCK"] = SocketClient("127.0.0.1", sock_ports["txdispatch"])

# type: obj -> str
def encode(data):
    return json.dumps(data)

# type: str -> obj
def decode(data):
    return json.loads(data)

@socketio.on("message")
def handle_message(message):
    print("[%s]> %s" % (time(), message))

@socketio.on("json")
def handle_json(json):
    print("[%s]> %s" % (time(), encode(json)))

@socketio.on("connected")
def handle_connected(hello):
    print("[%s]> %s" % (time(), encode(hello)))
    json = {
        "data": "Welcome to TxDispatch!"
    }
    emit("connected", json)

@socketio.on("request")
def handle_request(req):
    print("[%s]> %s" % (time(), encode(req)))
    name = req.get("name", None)
    data = req.get("data", None)
    
    if name is not None and data is not None:
        if name in list(services.keys()):
            ns = "/%s" % name
            dispatch = {
                "name": name,
                "data": data
            }
            dispatch["owner"] = request.sid
            handle_service_request(dispatch)
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

def handle_service_connected(hello):
    ns = request.namespace
    print("%s@[%s]> %s" % (ns[1:], time(), str(hello)))
    json = {
        "data": "Welcome to %s!" % ns[1:]
    }
    emit("connected", json, namespace=ns)
    
def handle_service_request(req):
    _ns = request.namespace
    print("%s@[%s]> %s" % (_ns[1:], time(), encode(req)))
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
    
for service, port in services.items():
    ns = "/%s" % service
    socketio.on_event("connected", handle_service_connected, namespace=ns)
    socketio.on_event("request", handle_service_request, namespace=ns)

if __name__ == "__main__":
    app.config["SOCK"].start()
    socketio.run(app, host="localhost", port=services["txdispatch"])
    #, debug=True)
