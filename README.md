# pyspoke

A python library supporting pubsub and remote procedure calls on Linux.

# Overview

This package provides a python library for passing JSON messages between processes. Clients publish messages to named channels and subscribe to channels to receive those messages. Each client connects to a single server that acts as the message broker. Features include:

- Hierarchical channel names with support for wildcard subscriptions
- Remote procedure calls built on top of the publish/subscribe capability
- Persistent messages that are recorded by the server and sent to clients that later subscribe to the channel
- Bridging servers so that they and their clients behave like a single network
- Customizable transport protocol - default is TCP sockets
- Asynchronous client/server code using standard asyncio module
- Synchronous wrapper functions for publish and rpc calls

# Installation

Requires Python 3.7 or greater

## From [PyPI](https://pypi.org/project/pyspoke/)

Install using pip:

```
python3 -m pip install pyspoke
```

## From latest source

First install build dependencies:

```
python3 -m pip install build
```

Building the distribution:

```
git clone https://gitlab.com/samflam/pyspoke.git
cd pyspoke
make
```

To install, you can `pip install` the built wheel in `dist` or simply run

```
make install
```

# Testing

From the top level, do:

```
make test
```

# Examples

## Basic publisher and subscriber

First we run the server that acts as a message broker, receiving published messages and sending them to subscribed clients:

```python
"Server code"
import asyncio
import spoke

server = spoke.pubsub.server.Server()

try:
    asyncio.run(server.run())
except KeyboardInterrupt:
    pass
```

Next we need a subscriber that will listen for messages on the given channel(s) and execute a callback function when a message is received. In this case we listen for messages on the `foo` channel and just print them out:

```python
"Subscriber"
import asyncio
import spoke

async def handle_foo(msg):
    print(f"Got message on foo channel: {msg.body}")

async def main():
    client = spoke.pubsub.client.Client()
    await client.run()
    await client.subscribe("foo", handle_foo)
    await spoke.wait()

asyncio.run(main())
```

Finally we publish a message on the `foo` channel. This example uses the synchonous wrapper function, which is simpler to use, but must establish a new connection each time it is called:

```python
"Publisher (using simple synchronous call)"
import spoke
spoke.publish("foo", 5)
```

# Command line interface

This package provides serveral command line scripts for common tasks. For help on any of them, run with the flag `-h`:

- `spoke-server` - runs a server that acts as the message broker
- `spoke-echo` - subscribes to the given channels and prints any messages that it receives
- `spoke-publish` - publish a message on the given channel
- `spoke-call` - do a remote procedure call on the given channel and print the result
- `spoke-bridge` - connect two spoke servers so that they and their clients transparently behave like a single network
