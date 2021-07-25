import asyncio
from spoke.message.client import Client


async def main():
    client = Client()
    await client.run()
    msg = {}
    await client.send(msg)
    msg = []
    await client.send(msg)
    msg = "junk"
    await client.send(msg)
    msg = {"head": None}
    await client.send(msg)
    msg = {"head": {}}
    await client.send(msg)
    msg = {
        "head": {
            "channel": ["this", "is", "junk"],
        },
    }
    await client.send(msg)


asyncio.run(main())
