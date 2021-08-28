"""Synchronous wrappers for one-time async spoke calls.
These have a lot of overhead setting up the scheduler and
creating a client, so if you need a persistent connection
it's far more efficient to use the async methods.

These methods must not be called while another asyncio
event loop is already running in the same thread.

"""
import asyncio
import os
import spoke


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
    conn_opts = {
        "host": host,
        "port": port,
    }
    client = spoke.pubsub.client.Client(conn_opts=conn_opts)
    result = [None]

    async def run():
        asyncio.create_task(client.run())
        awaitable = client.call(channel, body)

        if timeout:
            future = await asyncio.wait_for(awaitable, timeout)
        else:
            future = await awaitable
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
    conn_opts = {
        "host": host,
        "port": port,
    }
    client = spoke.pubsub.client.Client(conn_opts=conn_opts)

    async def run():
        asyncio.create_task(client.run())
        awaitable = client.publish(channel, body, **head)
        if timeout:
            await asyncio.wait_for(awaitable, timeout)
        else:
            await awaitable

    try:
        asyncio.run(run())
    except asyncio.TimeoutError as e:
        raise TimeoutError from e
