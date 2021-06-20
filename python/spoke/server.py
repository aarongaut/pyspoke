import os
import asyncio
import spoke

class ClientHandle:
    def __init__(self, reader, writer, server):
        self.reader = reader
        self.writer = writer
        self.server = server

    async def handle_recv(self):
        while True:
            try:
                msg_data = await self.reader.readuntil(separator=b'\0')
            except asyncio.exceptions.IncompleteReadError:
                # TODO: unsubscribe all
                break
            channel, msg = spoke.serialize.bytes_to_msg(msg_data)
            if channel == "spoke_control" and msg:
                self.server.subscribe(msg, self)
            if channel:
                await self.server.publish(channel, msg)

    async def send(self, channel, msg):
        msg_data = spoke.serialize.msg_to_bytes(channel, msg)
        self.writer.write(msg_data)
        await self.writer.drain()

class Server:
    def __init__(self, port=None):
        if port is None:
            port = os.getenv("SPOKEPORT", None) or 7181
        self._server = None
        self._subs = spoke.routing.SubscriberTable()
        self._port = port

    def subscribe(self, channel, client):
        self._subs.add_rule(channel, client)

    def unsubscribe(self, channel, client):
        self._subs.remove_rule(channel, client)

    async def publish(self, channel, msg):
        subs = self._subs.get_subs(channel)
        for sub in subs:
            await sub.send(channel, msg)

    async def run(self):
        self._server = await asyncio.start_server(self.handle_conn, "0.0.0.0", self._port)
        async with self._server:
            await self._server.serve_forever()

    async def handle_conn(self, reader, writer):
        client = ClientHandle(reader, writer, self)
        asyncio.create_task(client.handle_recv())
