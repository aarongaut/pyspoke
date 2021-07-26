import asyncio
import spoke


class _MessageClientPubSub(spoke.message.client.Client):
    def __init__(self, wrapper, host=None, port=None):
        super().__init__(host, port)
        self.__wrapper = wrapper

    async def handle_connect(self):
        for route in self.__wrapper._table.routes:
            await self.__wrapper.publish("-control/subscribe", route.channel())

    async def handle_recv(self, json_msg):
        msg = spoke.pubsub.msgpack.Message.unpack(json_msg)
        for destination in self.__wrapper._table.get_destinations(msg.channel):
            await destination(msg)


class Client:
    def __init__(self, host=None, port=None):
        self._table = spoke.pubsub.route.RoutingTable()
        self.__level2_client = _MessageClientPubSub(self, host, port)
        self.id = spoke.genid.uuid()

    async def run(self, timeout=None):
        await self.__level2_client.run(timeout=timeout)

    async def publish(self, channel, body, timeout=None, **head):
        json_msg = spoke.pubsub.msgpack.Message(channel, body, **head).pack()
        await self.__level2_client.send(json_msg, timeout=timeout)

    async def subscribe(self, channel, callback, timeout=None, **head):
        channel = spoke.pubsub.route.canonical(channel)
        await self.publish("-control/subscribe", channel, timeout=timeout, **head)
        rule = self._table.add_rule(channel, callback)

    async def unsubscribe(self, channel, timeout=None):
        channel = spoke.pubsub.route.canonical(channel)
        await self.publish("-control/unsubscribe", channel, timeout=timeout)
        rule = self._table.remove_rule(channel)

    async def provide(self, channel, callback, timeout=None):
        channel = spoke.pubsub.route.canonical(channel)

        async def _provide(call_msg):
            res_channel = call_msg.channel.rstrip("call") + "result"
            res_body = {}
            try:
                res_body["okay"] = await callback(call_msg)
            except Exception as e:
                res_body["error"] = str(e)
            await self.publish(res_channel, res_body)

        await self.subscribe(channel + "/-rpc/**/call", _provide, timeout=timeout)

    async def call(self, channel, body, timeout=None):
        future = asyncio.Future()
        channel = spoke.pubsub.route.canonical(channel)
        channel_head = "/".join([channel, "-rpc", self.id, spoke.genid.luid()])
        pub_channel = "/".join([channel_head, "call"])
        sub_channel = "/".join([channel_head, "result"])

        async def _handle_response(res_msg):
            if not future.done():
                if "okay" in res_msg.body:
                    future.set_result(res_msg.body["okay"])
                elif "error" in res_msg.body:
                    err = spoke.pubsub.error.RemoteCallError(res_msg.body["error"])
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
        await self.publish(pub_channel, body)
        return future
