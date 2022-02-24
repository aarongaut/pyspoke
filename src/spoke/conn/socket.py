import os
import asyncio
import socket

from . import abc

DEFAULT_PORT = 7181


class Connection(abc.AbstractConnection):
    RECV_BYTES = 2048

    def __init__(self, sock):
        self.__sock = sock
        self.__connected = True

    async def send(self, data: bytes):
        if not self.__connected:
            raise ConnectionError("Disconnected from server")
        loop = asyncio.get_running_loop()
        try:
            await loop.sock_sendall(self.__sock, data)
        except (ConnectionError, BrokenPipeError) as e:
            await self.close()
            raise ConnectionError("Disconnected from server") from e

    async def recv(self) -> bytes:
        if not self.__connected:
            raise ConnectionError("Disconnected from server")
        loop = asyncio.get_running_loop()
        try:
            ret = await loop.sock_recv(self.__sock, self.RECV_BYTES)
        except (ConnectionError, BrokenPipeError) as e:
            await self.close()
            raise ConnectionError("Disconnected from server") from e
        if not ret:
            await self.close()
            raise ConnectionError("Disconnected from server")
        return ret

    async def close(self):
        if self.__connected:
            self.__sock.close()
            self.__connected = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.recv()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


class Client(abc.AbstractClient):
    def __init__(self, host=None, port=None):
        host = host or os.getenv("SPOKEHOST", "localhost")
        port = port or int(os.getenv("SPOKEPORT", DEFAULT_PORT))
        self._address = (host, port)
        self._connection = None

    async def reset(self):
        "Close and forget the existing connection if one exists"
        loop = asyncio.get_running_loop()
        if self._connection is None:
            self._connection = loop.create_future()
        elif self._connection.done():
            try:
                await self._connection.result().close()
                self._connection = loop.create_future()
            except ConnectionError:
                pass

    async def connect(self) -> Connection:
        "Create a new connection, closing any existing one"
        await self.reset()
        loop = asyncio.get_running_loop()
        while True:
            sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK
            )
            try:
                await loop.sock_connect(sock, self._address)
                conn = Connection(sock)
                self._connection.set_result(conn)
                return conn
            except ConnectionError:
                await asyncio.sleep(0.1)
            except Exception as err:
                self._connection.set_exception(err)
                raise

    async def connection(self) -> Connection:
        """Get the connection, potentially waiting for it to be created
        via connect (on another task). Throws an error if the connection
        fails or if reset is called.

        """
        loop = asyncio.get_running_loop()
        if self._connection is None:
            self._connection = loop.create_future()
        return await self._connection

    def __aiter__(self):
        return self

    async def __anext__(self) -> Connection:
        return await self.connect()


class Server(abc.AbstractServer):
    def __init__(self, host=None, port=None, reuse=False):
        host = host or "0.0.0.0"
        port = port or int(os.getenv("SPOKEPORT", DEFAULT_PORT))
        self.__sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK
        )
        if reuse:
            self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((host, port))
        self.__sock.listen()
        self.__open = True

    def __aiter__(self):
        return self

    async def __anext__(self) -> Connection:
        return await self.accept()

    async def accept(self) -> Connection:
        loop = asyncio.get_running_loop()
        sock, _ = await loop.sock_accept(self.__sock)
        return Connection(sock)

    async def close(self):
        if self.__open:
            self.__open = False
            self.__sock.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
