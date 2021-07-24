import os
import asyncio

from .error import ExpectedConnectErrors, ExpectedReadErrors, ExpectedWriteErrors


class Client:
    def __init__(self, host=None, port=None):
        if host is None:
            host = os.getenv("SPOKEHOST", None) or "127.0.0.1"
        if port is None:
            port = os.getenv("SPOKEPORT", None) or 7181
        self.__host = host
        self.__port = port
        self.__connection = None
        self.__lock = None

    async def run(self, timeout=None):
        self.__lock = asyncio.Lock()
        if timeout:
            await asyncio.wait_for(self.__get_connection(), timeout=timeout)
        else:
            await self.__get_connection()
        self.__task = asyncio.create_task(self.__run_inner())

    async def handle_connect(self):
        pass

    async def handle_recv(self, data):
        pass

    async def handle_disconnect(self):
        pass

    async def __get_connection(self):
        async with self.__lock:
            required_connection = self.__connection is None
            while self.__connection is None:
                try:
                    self.__connection = await asyncio.open_connection(
                        self.__host, self.__port
                    )
                except ExpectedConnectErrors:
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print("UNEXPECTED CLIENT ERROR 1", type(e), e)
                    raise
        if required_connection:
            await self.handle_connect()
        return self.__connection

    async def __reset_connection(self):
        # Shut down connection?
        async with self.__lock:
            if self.__connection:
                _, writer = self.__connection
                writer.close()
                try:
                    await writer.wait_closed()
                except ExpectedReadErrors:
                    pass
                except Exception as e:
                    print("UNEXPECTED CLIENT ERROR 4", type(e), e)
                    raise
            self.__connection = None
        await self.handle_disconnect()

    async def __run_inner(self):
        while True:
            reader, _ = await self.__get_connection()
            try:
                data = await reader.read(1024)
                if data:
                    await self.handle_recv(data)
                else:
                    await self.__reset_connection()
            except ExpectedReadErrors:
                await self.__reset_connection()
            except Exception as e:
                print("UNEXPECTED CLIENT ERROR 2", type(e), e)
                raise

    async def send(self, data, timeout=None):
        if timeout:
            await asyncio.wait_for(self.__send_inner(data), timeout)
        else:
            await self.__send_inner(data)

    async def __send_inner(self, data):
        while True:
            _, writer = await self.__get_connection()
            try:
                writer.write(data)
                await writer.drain()
                return
            except ExpectedWriteErrors:
                await self.__reset_connection()
            except Exception as e:
                print("UNEXPECTED CLIENT ERROR 3", type(e), e)
                raise
