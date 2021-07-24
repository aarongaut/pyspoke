import asyncio
import spoke


async def invert(msg):
    return 1 / msg.body


async def main():
    client = spoke.pubsub.client.Client()
    await client.run()
    await client.provide("invert", invert)
    await spoke.wait.wait()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
