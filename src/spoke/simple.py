"""Synchronous wrappers for one-time async spoke calls.
These have a lot of overhead setting up the scheduler and
creating a client, so if you need a persistent connection
it's far more efficient to use the async methods.

These methods must not be called while another asyncio
event loop is already running in the same thread.

"""
import spoke
import asyncio


def call(channel, msg, host=None, port=None, timeout=None):
    client = spoke.pubsub.client.Client(host=host, port=port)
    result = [None]

    async def run():
        await client.run(timeout=timeout)
        future = await client.call(channel, msg, timeout=timeout)
        await future
        result[0] = future.result()

    try:
        asyncio.run(run())
    except asyncio.TimeoutError as e:
        raise TimeoutError from e
    return result[0]


def publish(channel, msg, host=None, port=None, timeout=None, **head):
    client = spoke.pubsub.client.Client(host=host, port=port)

    async def run():
        await client.run(timeout=timeout)
        await client.publish(channel, msg, timeout=timeout, **head)

    try:
        asyncio.run(run())
    except asyncio.TimeoutError as e:
        raise TimeoutError from e
