import asyncio
import spoke


async def main():
    client = spoke.conn.socket.Client()
    conn = await client.connect()
    msg = b"junk\x00"
    await conn.send(msg)
    msg = b"\xde\xad\xbe\xef\x00"
    await conn.send(msg)


asyncio.run(main())
