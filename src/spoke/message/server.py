import spoke
import json
import asyncio


class ConnectionSingleServerJSON(spoke.connection.server.SingleServer):
    def __init__(self, wrapper, reader, writer, context):
        super().__init__(reader, writer, context)
        self.__wrapper = wrapper
        self.__former = spoke.message.serialize.MessageFormer()

    async def handle_connect(self):
        await self.__wrapper.handle_connect()

    async def handle_disconnect(self):
        self.__former.reset()
        await self.__wrapper.handle_disconnect()

    async def handle_recv(self, data):
        self.__former.add_data(data)
        while self.__former.has_msg():
            data = self.__former.pop_msg()
            try:
                msg = spoke.message.serialize.bytes_to_msg(data)
            except (UnicodeDecodeError, json.decoder.JSONDecodeError) as e:
                msg = "Ignoring malformed message from client (not valid JSON): {}"
                print(msg.format(e))
            else:
                await self.__wrapper.handle_recv(msg)


class SingleServer:
    def __init__(self, reader, writer, context):
        self.__level1_single_server = ConnectionSingleServerJSON(
            self, reader, writer, context
        )
        self._context = context

    async def run(self):
        await self.__level1_single_server.run()

    async def send(self, msg):
        data = spoke.message.serialize.msg_to_bytes(msg)
        await self.__level1_single_server.send(data)

    async def handle_connect(self):
        pass

    async def handle_disconnect(self):
        pass

    async def handle_recv(self, msg):
        pass


class Server(spoke.connection.server.Server):
    def __init__(self, port=None, single_server_class=SingleServer):
        super().__init__(port, single_server_class)
