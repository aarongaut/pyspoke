import asyncio
import spoke

class Server(spoke.connection.server.Server):
    async def handle_connect(self, client):
        print("server.handle_connect")
    async def handle_disconnect(self, client):
        print("server.handle_disconnect")
    async def handle_recv(self, client, data):
        print("server.handle_recv: ", data)
        await self.broadcast(data)

server = Server()

asyncio.run(server.run())
