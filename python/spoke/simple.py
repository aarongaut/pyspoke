"""Synchronous wrappers for one-time async spoke calls.
These have a lot of overhead setting up the scheduler and
creating a client, so if you need a persistent connection
it's far more efficient to use the async methods.

These methods must not be called while another asyncio
event loop is already running in the same thread.

"""
import spoke
import asyncio

def call(channel, msg, host=None, port=None):
    client = spoke.pubsub.client.Client(host=host, port=port)
    result = [None]
    async def run():
        await client.run()
        future = await client.call(channel, msg)
        await future
        result[0] = future.result()
    asyncio.run(run(), debug=True)
    return result[0]

def publish(channel, msg, host=None, port=None):
    client = spoke.pubsub.client.Client(host=host, port=port)
    async def run():
        await client.run()
        await client.publish(channel, msg)
    asyncio.run(run(), debug=True)
