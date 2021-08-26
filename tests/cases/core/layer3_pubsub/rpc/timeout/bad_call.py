import asyncio
from spoke.pubsub.client import Client


async def main():
    client = Client()
    asyncio.create_task(client.run())
    val = await client.call("junk", None, timeout=2)
    try:
        await val
    except TimeoutError:
        print("Got expected TimeoutError")
    else:
        raise TestFailure("Didn't get a TimeoutError")


asyncio.run(main())
