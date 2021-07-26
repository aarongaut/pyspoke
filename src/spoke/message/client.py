import json
import os
import asyncio
import spoke


class _ConnectionClientJSON(spoke.connection.client.Client):
    def __init__(self, wrapper, host=None, port=None):
        super().__init__(host, port)
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
            except json.decoder.JSONDecodeError:
                print(
                    "Ignoring malformed message from server (not valid JSON): {}".format(
                        data
                    )
                )
            else:
                await self.__wrapper.handle_recv(msg)


class Client:
    def __init__(self, host=None, port=None):
        self.__level1_client = _ConnectionClientJSON(self, host, port)

    async def run(self, timeout=None):
        await self.__level1_client.run(timeout=timeout)

    async def send(self, msg, timeout=None):
        data = spoke.message.serialize.msg_to_bytes(msg)
        await self.__level1_client.send(data, timeout=timeout)

    async def handle_connect(self):
        pass

    async def handle_disconnect(self):
        pass

    async def handle_recv(self, msg):
        pass
