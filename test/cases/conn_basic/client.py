import sys
import os
import asyncio
import spoke

name = os.getenv("name", "unnamed")
count = int(os.getenv("count", 10))
delay = float(os.getenv("delay", 1))

class Client(spoke.connection.client.Client):
    async def handle_connect(self):
        print("Connected")
    async def handle_disconnect(self):
        print("Disconnected")
    async def handle_recv(self, data):
        print("recv: ", data.decode("utf8"))

async def main():
    client = Client()
    await client.run()
    for i in range(count):
        msg = "{} {}".format(name, i)
        print("sending: {}".format(msg))
        await client.send(msg.encode("utf8"))
        await asyncio.sleep(delay)

asyncio.run(main())
