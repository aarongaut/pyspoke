"""Synchronous wrappers for one-time async spoke calls.
These have a lot of overhead setting up the scheduler and
creating a client, so if you need a persistent connection
it's far more efficient to use the async methods.

These methods must not be called while another asyncio
event loop is already running in the same thread.

"""
import spoke
import asyncio


def call(channel, body, host=None, port=None, timeout=None):
    """Simple synchronous wrapper to do a remote procedure call (RPC)

    Raises
    ------
    TimeoutError
        If the timeout argument is given and exceeded
    spoke.pubsub.error.RemoteCallError
        If an error occurred when executing the RPC on the remote end

    See spoke.pubsub.client.Client.call for more details.

    """
    client = spoke.pubsub.client.Client(host=host, port=port)
    result = [None]

    async def run():
        await client.run(timeout=timeout)
        future = await client.call(channel, body, timeout=timeout)
        await future
        result[0] = future.result()

    try:
        asyncio.run(run())
    except asyncio.TimeoutError as e:
        raise TimeoutError from e
    return result[0]


def publish(channel, body, host=None, port=None, timeout=None, **head):
    """Simple synchronous wrapper to publish a message

    Raises
    ------
    TimeoutError
        If the timeout argument is given and exceeded

    See spoke.pubsub.client.Client.publish for more details.

    """
    client = spoke.pubsub.client.Client(host=host, port=port)

    async def run():
        await client.run(timeout=timeout)
        await client.publish(channel, body, timeout=timeout, **head)

    try:
        asyncio.run(run())
    except asyncio.TimeoutError as e:
        raise TimeoutError from e
