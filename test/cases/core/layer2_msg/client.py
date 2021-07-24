import sys
import os
import asyncio
import spoke

name = os.getenv("name", "unnamed")
count = int(os.getenv("count", 10))
delay = float(os.getenv("delay", 1))


class Client(spoke.message.client.Client):
    async def handle_connect(self):
        print("Connected")

    async def handle_disconnect(self):
        print("Disconnected")

    async def handle_recv(self, msg):
        print("recv value: ", msg["value"])


async def main():
    client = Client()
    await client.run()
    for i in range(count):
        msg = {"name": name, "value": i}
        print("sending: {}".format(i))
        await client.send(msg)
        await asyncio.sleep(delay)


asyncio.run(main())
