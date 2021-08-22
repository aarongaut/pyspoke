import asyncio
import json
from . import abc


class TrivialPacker(abc.AbstractPacker):
    def __init__(self):
        self.__buffer = []

    def pack(self, msg):
        data = msg
        return data

    def unpack(self, data):
        self.__buffer.append(data)

    def reset(self):
        self.__buffer.clear()

    def __iter__(self):
        return self

    def __next__(self):
        if self.__buffer:
            msg = self.__buffer.pop(0)
            return msg
        else:
            raise StopIteration


class JsonPacker(abc.AbstractPacker):
    MSG_SEP = b"\x00"

    def __init__(self):
        self.__fragments = []
        self.__messages = []

    def pack(self, msg):
        msg = json.dumps(msg)
        return msg.encode("utf8") + b"\0"

    def unpack(self, data):
        if self.MSG_SEP in data:
            end_frag, *msg_datas, begin_frag = data.split(self.MSG_SEP)
            self.__fragments.append(end_frag)
            msg_data = b"".join(self.__fragments)
            self.__messages.append(json.loads(msg_data))
            for msg_data in msg_datas:
                self.__messages.extend(json.loads(msg_data))
            self.__fragments = [begin_frag]
        else:
            self.__fragments.append(data)

    def reset(self):
        self.__fragments.clear()
        self.__messages.clear()

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__messages:
            raise StopIteration
        return self.__messages.pop(0)


class Connection(abc.AbstractConnection):
    def __init__(self, conn: abc.AbstractConnection, packer: abc.AbstractPacker):
        self.__conn = conn
        self.__packer = packer

    async def send(self, msg):
        await self.__conn.send(self.__packer.pack(msg))

    async def recv(self):
        while True:
            try:
                return next(self.__packer)
            except StopIteration:
                pass
            self.__packer.unpack(await self.__conn.__anext__())

    async def close(self):
        await self.__conn.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.recv()


class Client(abc.AbstractClient):
    def __init__(self, conn_client_class, packer_class=TrivialPacker, **kwargs):
        self.__conn_client = conn_client_class(**kwargs)
        self.__packer = packer_class()

    async def reset(self):
        await self.__conn_client.reset()
        self.__packer.reset()

    async def connection(self) -> Connection:
        return Connection(await self.__conn_client.connection(), self.__packer)

    async def connect(self) -> Connection:
        await self.reset()
        conn = await self.__conn_client.__anext__()
        return Connection(conn, self.__packer)

    def __aiter__(self):
        return self

    async def __anext__(self) -> Connection:
        return await self.connect()


class Server(abc.AbstractServer):
    def __init__(self, conn_server_class, packer_class=TrivialPacker, **kwargs):
        self.__conn_server = conn_server_class(**kwargs)
        self.__packer_class = packer_class

    def __aiter__(self):
        return self

    async def __anext__(self) -> Connection:
        return await self.accept()

    async def accept(self) -> Connection:
        conn = await self.__conn_server.accept()
        return Connection(conn, self.__packer_class())

    async def close(self):
        await self.__conn_server.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
