import configparser
import os

basedir = os.path.abspath(os.path.dirname(__file__))
config = configparser.ConfigParser()
config.read("txdispatch.conf")
SECRET_KEY = config.get("app", "secret_key")
VERSION = config.get("app", "version")
SERVICES = {
    "http": {},
    "sockets": {},
    "websockets": {}
}

for service, port in config.items("services"):
    SERVICES["http"][service] = int(port)
    SERVICES["sockets"][service] = int(port) + 10
    SERVICES["websockets"][service] = int(port) + 20
