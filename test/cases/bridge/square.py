import asyncio
import spoke


async def square(channel, msg):
    return msg * msg


async def main():
    client = spoke.pubsub.client.Client()
    await client.run()
    await client.provide("square", square)
    await spoke.wait.wait()


asyncio.run(main())
