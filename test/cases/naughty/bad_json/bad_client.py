import asyncio
from spoke.connection.client import Client


async def main():
    client = Client()
    await client.run()
    msg = b"junk\x00"
    await client.send(msg)
    msg = b"\xde\xad\xbe\xef\x00"
    await client.send(msg)


asyncio.run(main())
