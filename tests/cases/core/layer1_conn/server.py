import os
import asyncio
import spoke


host = os.getenv("SPOKEHOST", "127.0.0.1")
port = int(os.getenv("SPOKEPORT", 7181))

clients = []

async def handle_client(conn):
    clients.append(conn)
    print("server.handle_connect")
    try:
        async for msg in conn:
            print(f"server.handle_recv: {msg}")
            for client in clients:
                await client.send(msg)
    except ConnectionError:
        pass
    finally:
        print("server.handle_disconnect")
        clients.remove(conn)

async def main():
    async with spoke.conn.socket.Server(address=(host, port), reuse=True) as server:
        async for client in server:
            asyncio.create_task(handle_client(client))

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
