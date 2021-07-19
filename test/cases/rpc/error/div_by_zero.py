import asyncio
from spoke.pubsub.client import Client
from spoke.pubsub.error import RemoteCallError


class TestFailure(AssertionError):
    pass

async def main():
    client = Client()
    await client.run()
    val = await client.call("invert", 0)
    try:
        await val
    except RemoteCallError as e:
        msg = "Got expected error: {}"
        print(msg.format(e))
    else:
        raise TestFailure("Didn't get expected error")


asyncio.run(main())
