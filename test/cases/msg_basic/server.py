import asyncio
import spoke

class SingleServer(spoke.message.server.SingleServer):
    async def handle_connect(self):
        print("server.handle_connect")
        if "clients" not in self._context:
            self._context["clients"] = []
        self._context["clients"].append(self)

    async def handle_disconnect(self):
        print("server.handle_disconnect")
        self._context["clients"].remove(self)

    async def handle_recv(self, data):
        print("server.handle_recv: ", data)
        for client in self._context["clients"]:
            await client.send(data)

server = spoke.message.server.Server(single_server_class=SingleServer)

asyncio.run(server.run())
