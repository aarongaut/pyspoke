import asyncio
import spoke

client = spoke.pubsub.client.Client()
# Using a deterministic id to produce consistent output for comparison
client.id = "caller_id"


async def main():
    await client.run()
    result = await client.call("square", 5)
    print(result)


asyncio.run(main())
