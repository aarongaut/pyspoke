import asyncio
from spoke.client import Client

async def square(channel, msg):
    return msg * msg

async def main():
    client = Client()
    await client.run()
    await client.provide("square", square)
    await client.wait()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass