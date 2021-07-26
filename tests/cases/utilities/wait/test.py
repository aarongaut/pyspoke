import asyncio
import spoke


async def main():
    await spoke.wait()
    print("Exiting")


asyncio.run(main())
