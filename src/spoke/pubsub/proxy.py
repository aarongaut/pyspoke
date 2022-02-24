import time
import json
import asyncio
import dataclasses
import spoke
from .route import RoutingTable
from .client import Client


@dataclasses.dataclass
class ClientData:
    conn: spoke.conn.pack.Connection
    routing_table: RoutingTable
    control_table: RoutingTable


class Server:
    def __init__(self, allowed_channels, conn_client_class=spoke.conn.socket.Client, conn_client_opts=None, conn_server_class=spoke.conn.socket.Server, conn_server_opts=None):
        self.__conn_server = spoke.conn.pack.Server(
            conn_server_class,
            spoke.pubsub.pack.MessagePacker,
            conn_opts=conn_server_opts,
        )
        self.__allowlist = allowed_channels
        self.__proxy_client = Client(conn_client_class, conn_client_opts)
        self.__id = spoke.genid.uuid()
        self.__state = {}
        self.__clients = {}

    async def run(self):
        await self.__proxy_client.run()

        async def _handle_proxy_client_msg(msg):
            self.__state[msg.channel] = msg
            for client_id, client_data in self.__clients.items():
                if client_data.routing_table.get_destinations(msg.channel):
                    await client_data.conn.send(msg)

        for channel in self.__allowlist:
            await self.__proxy_client.subscribe(channel, _handle_proxy_client_msg)

        async for client in self.__conn_server:
            asyncio.create_task(self.__handle_client(client))

    async def __handle_client(self, client):
        client_id = spoke.genid.luid()
        data = ClientData(
            conn=client,
            control_table=RoutingTable(),
            routing_table=RoutingTable(),
        )
        self.__clients[client_id] = data

        async def _subscribe(channel):
            channel = spoke.pubsub.route.canonical(channel)
            route = data.routing_table.add_rule(channel)
            for pchannel, msg in self.__state.items():
                if route.test(spoke.pubsub.route.tokenize(pchannel)):
                    await client.send(msg)

        async def _unsubscribe(channel):
            channel = spoke.pubsub.route.canonical(channel)
            data.routing_table.remove_rule(channel)

        data.control_table.add_rule("-control/subscribe", _subscribe)
        data.control_table.add_rule("-control/unsubscribe", _unsubscribe)

        async def msggen():
            while True:
                try:
                    msg = await client.recv()
                except (UnicodeDecodeError, json.decoder.JSONDecodeError) as e:
                    print(
                        f"Ignoring malformed message from client (not valid JSON): {e}"
                    )
                except ValueError as e:
                    print(f"Ignoring malformed message from client: {e}")
                else:
                    yield msg

        try:
            async for msg in msggen():
                for destination in data.control_table.get_destinations(msg.channel):
                    await destination(msg.body)

        except ConnectionError:
            del self.__clients[client_id]
