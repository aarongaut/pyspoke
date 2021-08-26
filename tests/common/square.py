import asyncio
import spoke


async def square(msg):
    return msg.body * msg.body


async def main():
    client = spoke.pubsub.client.Client()
    asyncio.create_task(client.run())
    await client.provide("square", square)
    await spoke.wait()


asyncio.run(main())
