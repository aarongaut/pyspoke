import sys
import os
import asyncio
import spoke

name = os.getenv("name", "unnamed")
count = int(os.getenv("count", 10))
delay = float(os.getenv("delay", 1))

host = os.getenv("SPOKEHOST", "127.0.0.1")
port = int(os.getenv("SPOKEPORT", 7181))

async def main():
    conn = await spoke.conn.pack.Client(
        conn_client_class = spoke.conn.socket.Client,
        packer_class = spoke.conn.pack.JsonPacker,
        address=(host, port)
    ).connect()
    print("Connected")

    async def echo(conn):
        try:
            async for msg in conn:
                print(f"recv value: {msg['value']}")
        except ConnectionError:
            pass
        print("Disconnected")

    asyncio.create_task(echo(conn))

    try:
        for i in range(count):
            msg = {"name": name, "value": i}
            print(f"sending: {msg['value']}")
            await conn.send(msg)
            await asyncio.sleep(delay)
    except ConnectionError:
        pass

asyncio.run(main())
