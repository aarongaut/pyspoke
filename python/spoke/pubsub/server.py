import spoke
import asyncio


class MessageSingleServerPubSub(spoke.message.server.SingleServer):
    def __init__(self, wrapper, reader, writer, context):
        super().__init__(reader, writer, context)
        self.__wrapper = wrapper
        self.__control_table = spoke.pubsub.route.RoutingTable()
        self.__context = context
        self._bounce = True
        self._table = spoke.pubsub.route.RoutingTable()

        if "clients" not in context:
            self.__context["clients"] = []

        def _subscribe(channel):
            if isinstance(channel, str):
                channel = spoke.pubsub.route.canonical(channel)
                self._table.add_rule(channel)

        def _unsubscribe(channel):
            if isinstance(channel, str):
                channel = spoke.pubsub.route.canonical(channel)
                self._table.remove_rule(channel)

        def _bounce(flag):
            self._bounce = bool(flag)

        self.__control_table.add_rule("-control/subscribe", _subscribe)
        self.__control_table.add_rule("-control/unsubscribe", _unsubscribe)
        self.__control_table.add_rule("-control/bounce", _bounce)

    async def handle_connect(self):
        self._context["clients"].append(self)

    async def handle_disconnect(self):
        self._context["clients"].remove(self)

    async def handle_recv(self, json_msg):
        try:
            msg = spoke.pubsub.msgpack.Message.unpack(json_msg)
        except ValueError as e:
            err_msg = "Ignoring malformed message from client: {}"
            print(err_msg.format(e))
        else:
            for destination in self.__control_table.get_destinations(msg.channel):
                destination(msg.body)
            to_json_msg = msg.pack()
            for client in self._context["clients"]:
                if client == self and not self._bounce:
                    continue
                if client._table.get_destinations(msg.channel):
                    await client.send(to_json_msg)


class SingleServer:
    def __init__(self, reader, writer, context):
        self.__level2_single_server = MessageSingleServerPubSub(
            self, reader, writer, context
        )

    async def run(self):
        await self.__level2_single_server.run()


class Server(spoke.message.server.Server):
    def __init__(self, port=None, single_server_class=SingleServer):
        super().__init__(port, single_server_class)
