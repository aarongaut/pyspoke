import asyncio
from spoke.message.client import Client


async def main():
    client = Client()
    await client.run()
    msg = {
        "channel": ["this", "is", "junk"],
        "payload": None,
    }
    await client.send(msg)
    msg = {"payload": None}
    await client.send(msg)
    msg = {"chennel": "foo"}
    await client.send(msg)
    msg = {"chennel": "foo", "foo": "bar"}
    await client.send(msg)


asyncio.run(main())
