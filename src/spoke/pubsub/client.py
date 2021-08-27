import asyncio
import spoke


class Client:
    def __init__(self, conn_client_class=spoke.conn.socket.Client, conn_opts=None, on_connect=None):
        self._conn_client = spoke.conn.pack.Client(
            conn_client_class,
            spoke.pubsub.pack.MessagePacker,
            conn_opts=conn_opts,
        )
        self._table = spoke.pubsub.route.RoutingTable()
        self.id = spoke.genid.uuid()
        self._on_connect = on_connect

    async def run(self):
        async def _run():
            async for conn in self._conn_client:
                try:
                    if self._on_connect:
                        await self._on_connect(conn)
                    subs = []
                    for route in self._table.routes:
                        subs.append(
                            self.publish("-control/subscribe", route.channel(), retry=False)
                        )
                    await asyncio.gather(*subs)
                    async for msg in conn:
                        cbs = [d(msg) for d in self._table.get_destinations(msg.channel)]
                        await asyncio.gather(*cbs)
                except ConnectionError:
                    pass
        asyncio.create_task(_run())

    async def publish(self, channel, body, retry=True, **head):
        """Note: retry needs to be False when publishing in a subscribe
        callback to avoid a deadlock if the connection fails

        """
        msg = spoke.pubsub.pack.Message(channel, body, **head)
        while True:
            conn = await self._conn_client.connection()
            try:
                await conn.send(msg)
            except ConnectionError:
                if not retry:
                    raise
            else:
                break

    async def subscribe(self, channel, callback, **head):
        channel = spoke.pubsub.route.canonical(channel)
        await self.publish("-control/subscribe", channel, **head)
        rule = self._table.add_rule(channel, callback)

    async def unsubscribe(self, channel):
        channel = spoke.pubsub.route.canonical(channel)
        await self.publish("-control/unsubscribe", channel)
        rule = self._table.remove_rule(channel)

    async def provide(self, channel, callback):
        channel = spoke.pubsub.route.canonical(channel)

        async def _provide(call_msg):
            res_channel = call_msg.channel.rstrip("call") + "result"
            res_body = {}
            try:
                res_body["okay"] = await callback(call_msg)
            except Exception as e:
                res_body["error"] = str(e)
            await self.publish(res_channel, res_body, retry=False)

        await self.subscribe(channel + "/-rpc/**/call", _provide)

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

        # TODO: remove timeout arg and somehow automatically unsubscribe
        # if cancelled
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
