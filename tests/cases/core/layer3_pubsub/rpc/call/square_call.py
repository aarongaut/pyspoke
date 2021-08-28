import asyncio
from spoke.pubsub.client import Client

arg = 5


async def main():
    client = Client()
    await client.run()
    val = await client.call("square", arg)
    print("{}**2 = {}".format(arg, val))


asyncio.run(main())
