import asyncio
from abc import ABC, abstractmethod


class AbstractConnection(ABC):
    @abstractmethod
    async def send(self, msg):
        pass

    @abstractmethod
    async def recv(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    def __aiter__(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self):
        pass


class AbstractClient(ABC):
    @abstractmethod
    async def connect(self) -> AbstractConnection:
        pass

    @abstractmethod
    async def connection(self) -> AbstractConnection:
        pass

    @abstractmethod
    async def reset(self):
        pass

    @abstractmethod
    def __aiter__(self):
        pass


class AbstractPacker(ABC):
    @abstractmethod
    def pack(self, msg):
        pass

    @abstractmethod
    def unpack(self, data):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def reset(self):
        pass


class AbstractServer(ABC):
    @abstractmethod
    def __aiter__(self):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self):
        pass

    @abstractmethod
    async def accept(self) -> AbstractConnection:
        pass

    @abstractmethod
    async def close(self):
        pass
