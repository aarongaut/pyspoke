import asyncio
import spoke

client = spoke.pubsub.client.Client()
# Using a deterministic id for output comparison
client.id = "caller_id"


async def main():
    await client.run()
    future = await client.call("square", 5, timeout=1)
    await future
    print(future.result())


asyncio.run(main())
