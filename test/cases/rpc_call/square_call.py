import asyncio
from spoke.pubsub.client import Client

arg = 5


async def main():
    client = Client()
    await client.run()
    val = await client.call("square", arg)
    await val
    print("{}**2 = {}".format(arg, val.result()))


asyncio.run(main())
