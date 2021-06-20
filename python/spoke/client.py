import os
import asyncio
from spoke import serial

class Client:
    def __init__(self, host=None, port=None):
        if host is None:
            host = os.getenv("SPOKEHOST", None) or "localhost"
        if port is None:
            port = os.getenv("SPOKEPORT", None) or 8888

        self.connected = False
        self.reader = None
        self.writer = None
        self.port = port
        self.host = host
        self.subs = {}

    async def publish(self, channel, msg):
        msg_data = serial.msg_to_bytes(channel, msg)
        self.writer.write(msg_data)
        await self.writer.drain()

    async def subscribe(self, channel, callback):
        if channel not in self.subs:
            await self.publish("spoke_control", channel)
        self.subs[channel] = callback

    async def unsubscribe(self, channel):
        # TODO: tell server
        if channel in self.subs:
            del self.subs[channel]

    async def run(self, wait=False):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        self.connected = True
        self.reader = reader
        self.writer = writer
        asyncio.create_task(self._listen())
        if wait:
            await self.wait()

    async def wait(self):
        while self.connected:
            await asyncio.sleep(1)

    async def _listen(self):
        while True:
            try:
                msg_data = await self.reader.readuntil(separator=b"\0")
            except asyncio.exceptions.IncompleteReadError:
                self.connected = False
                break
            channel, msg = serial.bytes_to_msg(msg_data)
            if channel in self.subs:
                await self.subs[channel](msg)
