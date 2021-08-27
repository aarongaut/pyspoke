import time
import json
import asyncio
import dataclasses
import spoke
from .route import RoutingTable


@dataclasses.dataclass
class ClientData:
    conn: spoke.conn.pack.Connection
    routing_table: RoutingTable
    control_table: RoutingTable


class Server:
    def __init__(self, conn_server_class=spoke.conn.socket.Server, conn_opts=None):
        self.__conn_server = spoke.conn.pack.Server(
            conn_server_class,
            spoke.pubsub.pack.MessagePacker,
            conn_opts=conn_opts,
        )
        self.__id = spoke.genid.uuid()
        self.__state = {}
        self.__clients = {}

    async def run(self):
        async for client in self.__conn_server:
            asyncio.create_task(self.__handle_client(client))

    @staticmethod
    def __massage_head(msg):
        """Prepares a message to be published to clients. The message
        is modified in place, and a dictionary of extracted server
        hints is returned.

        """
        if "time" not in msg.head:
            msg.head["time"] = time.time()
        hints = {
            "bounce": msg.head.get("bounce", True),
            "persist": msg.head.get("persist", False),
            "time": msg.head["time"],
        }
        if "bounce" in msg.head:
            del msg.head["bounce"]
        return hints

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
                hints = self.__massage_head(msg)

                if hints["persist"]:
                    last_msg = self.__state.get(msg.channel, None)
                    if last_msg is None or last_msg.head["time"] < hints["time"]:
                        self.__state[msg.channel] = msg
                    elif last_msg.head["time"] >= hints["time"]:
                        # Discarding old message
                        continue

                for peer_id, peer_data in self.__clients.items():
                    if peer_id == client_id and not hints["bounce"]:
                        continue
                    if peer_data.routing_table.get_destinations(msg.channel):
                        await peer_data.conn.send(msg)

        except ConnectionError:
            del self.__clients[client_id]
