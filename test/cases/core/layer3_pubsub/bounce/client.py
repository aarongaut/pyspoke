import asyncio
import spoke

client = spoke.pubsub.client.Client()


async def echo(msg):
    print(msg.body)


async def main():
    await client.run()
    await client.subscribe("test", echo)
    await client.publish("test", 1, bounce=False)
    await client.publish("test", 2)
    await client.publish("test", 3, bounce=False)
    await client.publish("test", 4)
    await client.publish("test", 5, bounce=False)
    await asyncio.sleep(0.2)


asyncio.run(main())
