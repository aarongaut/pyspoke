import asyncio
import spoke


async def main():
    client = spoke.conn.pack.Client(
        conn_client_class=spoke.conn.socket.Client,
        packer_class=spoke.conn.pack.JsonPacker,
    )

    conn = await client.connect()
    msg = {}
    await conn.send(msg)
    msg = []
    await conn.send(msg)
    msg = "junk"
    await conn.send(msg)
    msg = {"head": None}
    await conn.send(msg)
    msg = {"head": {}}
    await conn.send(msg)
    msg = {
        "head": {
            "channel": ["this", "is", "junk"],
        },
    }
    await conn.send(msg)


asyncio.run(main())
