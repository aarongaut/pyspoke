import asyncio
import os

from .error import ExpectedReadErrors, ExpectedWriteErrors

class ClientProxy:
    def __init__(self, server, reader, writer):
        self.__server = server
        self.__reader = reader
        self.__writer = writer

    async def run(self):
        while True:
            try:
                data = await self.__reader.read(1024)
                if data:
                    await self.__server.handle_recv(self, data)
                else:
                    await self.shutdown()
                    return
            except ExpectedReadErrors:
                await self.shutdown()
                return
            except Exception as e:
                print("UNEXPECTED SERVER ERROR 1", type(e), e)
                raise

    async def shutdown(self):
        # close connection?
        await self.__server.on_disconnect(self)

    async def send(self, data):
        try:
            self.__writer.write(data)
            await self.__writer.drain()
        except ExpectedWriteErrors:
            await self.shutdown()
        except Exception as e:
            print("UNEXPECTED SERVER ERROR 2", type(e), e)
            raise

class Server:
    def __init__(self, port=None):
        if port is None:
            port = os.getenv("SPOKEPORT", None) or 7181
        self.__asyncio_server = None
        self.__clients = []
        self.__port = port

    async def run(self):
        self.__asyncio_server = await asyncio.start_server(self.on_connect, "0.0.0.0", self.__port)
        async with self.__asyncio_server:
            await self.__asyncio_server.serve_forever()

    async def on_disconnect(self, client):
        self.__clients.remove(client)
        await self.handle_disconnect(client)

    async def broadcast(self, data):
        for client in self.__clients:
            await client.send(data)

    async def on_connect(self, reader, writer):
        client = ClientProxy(self, reader, writer)
        self.__clients.append(client)
        asyncio.create_task(client.run())
        await self.handle_connect(client)

    async def handle_disconnect(self, client):
        pass

    async def handle_recv(self, client, data):
        pass

    async def handle_connect(self, client):
        pass

