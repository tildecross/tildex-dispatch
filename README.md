Tildex :: Dispatch
==================

Tildex :: Dispatch, aka TxDispatch, is a service designed to manage 
communication between Tildecross services using it's unique architecture. The 
structure of Tildecross's communication architecture is as follows:
* Service-to-Client: Websockets
* Service-to-Service (internal): OS Sockets
* Service-to-Service (external): HTTP API

This allows for the most efficient path of data to be utilized based upon the 
relationship of where the data needs to go. To keep consistency across the 
different protocols, the data passed along will be in JSON in the following 
format:
```javascript
{
 "name": String,
 "data": String | Object
}
```
The **name** parameter is used to specify the context of the message from a 
pre-defined list (presently `connected` and `request`) when sent to TxDispatch 
and will otherwise be the service meant to receive the message. The **data** 
parameter will either be a single string for singular messages and will 
otherwise be an object of values meant for the recipient to handle. 

It is not recommended to use TxDispatch for sending sensitive data, but rather 
for sharing resources among other services to expand the functionality and 
usefulness of the Tildecross Development Suite.

Installation
------------

After downloading / cloning the repository, create the virtual environment for 
Python 3 in the same directory as the project and activate it.

```bash
$ python3 -m venv env
$ . env/bin/activate
```

You'll then want to install the dependencies for TxDispatch.

```bash
$ pip3 install -r requirements.txt
```

After that, create the config file from the example and fill it out based upon 
the Tildecross services you are using and the `secret_key` for TxDispatch to 
use.

```bash
$ cp txdispatch.example.conf txdispatch.conf
```

Once that is done, you'll want to first start the socket server followed by the 
TxDispatch service (ideally in separate windows / tabs to better monitor them).

```bash
$ chmod a+x sockets.py && chmod a+x run.py
$ ./sockets.py

$ ./run.py
```

Then once any services that are compatible with TxDispatch are run, 
they can use the Tildecross Communication Architecture to share resources among 
themselves.
