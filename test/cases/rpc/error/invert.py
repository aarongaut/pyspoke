import asyncio
from spoke.pubsub.client import Client


async def invert(channel, msg):
    return 1 / msg


async def main():
    client = Client()
    await client.run()
    await client.provide("invert", invert)
    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
