import asyncio
import spoke


class MessageClientPubSub(spoke.message.client.Client):
    def __init__(self, wrapper, host=None, port=None):
        super().__init__(host, port)
        self.__wrapper = wrapper
        self.__bounce = True

    async def handle_connect(self):
        for route in self.__wrapper._table.routes:
            await self.__wrapper.publish("-control/subscribe", route.channel())
        if not self.__bounce:
            self.__wrapper.publich("-control/bounce", False)

    async def handle_recv(self, msg):
        channel, payload = spoke.pubsub.msgpack.unpack_msg(msg)
        for destination in self.__wrapper._table.get_destinations(channel):
            await destination(channel, payload)


class Client:
    def __init__(self, host=None, port=None):
        self._table = spoke.pubsub.route.RoutingTable()
        self.__level2_client = MessageClientPubSub(self, host, port)
        self.id = spoke.genid.uuid()

    async def run(self):
        await self.__level2_client.run()

    async def publish(self, channel, payload):
        full_msg = spoke.pubsub.msgpack.pack_msg(channel, payload)
        await self.__level2_client.send(full_msg)

    async def subscribe(self, channel, callback):
        rule = self._table.add_rule(channel, callback)
        await self.publish("-control/subscribe", rule.channel())

    async def unsubscribe(self, channel):
        rule = self._table.remove_rule(channel)
        await self.publish("-control/unsubscribe", rule.channel())

    async def bounce(self, flag):
        """If False, tells the server not to send back messages
        published by this client, even if this client is subscribed
        to that channel.

        """
        self.__bounce = bool(flag)
        await self.publish("-control/bounce", bool(self.__bounce))

    async def provide(self, channel, callback):
        channel = spoke.pubsub.route.canonical(channel)

        async def _provide(call_channel, call_payload):
            res_channel = call_channel.rstrip("call") + "result"
            res_payload = {}
            try:
                res_payload["okay"] = await callback(call_channel, call_payload)
            except Exception as e:
                res_payload["error"] = str(e)
            await self.publish(res_channel, res_payload)

        await self.subscribe(channel + "/-rpc/**/call", _provide)

    async def call(self, channel, payload, timeout=None):
        future = asyncio.Future()
        channel = spoke.pubsub.route.canonical(channel)
        channel_head = "/".join([channel, "-rpc", self.id, spoke.genid.luid()])
        pub_channel = "/".join([channel_head, "call"])
        sub_channel = "/".join([channel_head, "result"])

        async def _handle_response(_, res_msg):
            if not future.done():
                if "okay" in res_msg:
                    future.set_result(res_msg["okay"])
                elif "error" in res_msg:
                    err = spoke.pubsub.error.RemoteCallError(res_msg["error"])
                    future.set_exception(err)
                else:
                    err = spoke.pubsub.error.RemoteCallError("Malformed response")
                    future.set_exception(err)
                await self.unsubscribe(sub_channel)

        if timeout:

            async def _handle_timeout():
                await asyncio.sleep(timeout)
                if not future.done():
                    future.set_exception(TimeoutError())
                    await self.unsubscribe(sub_channel)

            asyncio.create_task(_handle_timeout())

        await self.subscribe(sub_channel, _handle_response)
        await self.publish(pub_channel, payload)
        return future
