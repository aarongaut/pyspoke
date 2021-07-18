import asyncio
from spoke.pubsub.client import Client


async def square(channel, msg):
    return msg * msg


async def main():
    client = Client()
    await client.run()
    await client.provide("square", square)
    while True:
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
