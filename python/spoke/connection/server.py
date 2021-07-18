import asyncio
import os

from .error import ExpectedReadErrors, ExpectedWriteErrors


class SingleServer:
    def __init__(self, reader, writer, context):
        self.__reader = reader
        self.__writer = writer
        self._context = context

    async def run(self):
        await self.handle_connect()
        while True:
            try:
                data = await self.__reader.read(1024)
                if data:
                    await self.handle_recv(data)
                else:
                    await self.__shutdown()
                    return
            except ExpectedReadErrors:
                await self.__shutdown()
                return
            except Exception as e:
                print("UNEXPECTED SERVER ERROR 1", type(e), e)
                raise

    async def __shutdown(self):
        # close connection?
        self.__writer.close()
        try:
            await self.__writer.wait_closed()
        except ExpectedReadErrors:
            pass
        except Exception as e:
            print("UNEXPECTED CLIENT ERROR 4", type(e), e)
            raise
        await self.handle_disconnect()

    async def send(self, data):
        try:
            self.__writer.write(data)
            await self.__writer.drain()
        except ExpectedWriteErrors:
            await self.__shutdown()
        except Exception as e:
            print("UNEXPECTED SERVER ERROR 2", type(e), e)
            raise

    async def handle_recv(self, data):
        pass

    async def handle_connect(self):
        pass

    async def handle_disconnect(self):
        pass


class Server:
    def __init__(self, port=None, single_server_class=SingleServer):
        if port is None:
            port = os.getenv("SPOKEPORT", None) or 7181
        self.__asyncio_server = None
        self.__port = port
        self.__single_server_class = single_server_class
        self.__context = {}

    async def run(self):
        self.__asyncio_server = await asyncio.start_server(
            self.on_connect, "0.0.0.0", self.__port
        )
        async with self.__asyncio_server:
            await self.__asyncio_server.serve_forever()

    async def on_connect(self, reader, writer):
        client = self.__single_server_class(reader, writer, self.__context)
        asyncio.create_task(client.run())
