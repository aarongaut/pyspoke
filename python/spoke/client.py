import os
import asyncio
import spoke

class Client:
    def __init__(self, host=None, port=None):
        if host is None:
            host = os.getenv("SPOKEHOST", None) or "localhost"
        if port is None:
            port = os.getenv("SPOKEPORT", None) or 7181

        self.connected = False
        self.reader = None
        self.writer = None
        self.port = port
        self.host = host
        self.id = spoke.genid.uuid()
        self.subs = spoke.routing.SubscriberTable()

    async def publish(self, channel, msg):
        msg_data = spoke.serialize.msg_to_bytes(channel, msg)
        self.writer.write(msg_data)
        await self.writer.drain()

    async def subscribe(self, channel, callback):
        cb_id = spoke.genid.luid()
        self.subs.add_rule(channel, callback, cb_id)
        await self.publish("spoke_control", channel)
        return cb_id

    async def unsubscribe(self, cb_id):
        # TODO: tell server
        self.subs.remove_sub(cb_id)

    async def provide(self, channel, callback):
        async def _provide(call_channel, msg):
            res_val = await callback(call_channel, msg)
            res_channel = call_channel.rstrip("call") + "result"
            await self.publish(res_channel, res_val)
        await self.subscribe(channel + "/**/call", _provide)

    async def call(self, channel, msg):
        future = asyncio.Future()
        channel_head = "/".join([channel, self.id, spoke.genid.luid()])
        pub_channel = "/".join([channel_head, "call"])
        sub_channel = "/".join([channel_head, "result"])
        sub_id = [None]
        async def _call(_, res_msg):
            future.set_result(res_msg)
            await self.unsubscribe(sub_id[0])
        sub_id[0] = await self.subscribe(sub_channel, _call)
        await self.publish(pub_channel, msg)
        return future


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
            channel, msg = spoke.serialize.bytes_to_msg(msg_data)
            for callback in self.subs.get_subs(channel):
                await callback(channel, msg)
