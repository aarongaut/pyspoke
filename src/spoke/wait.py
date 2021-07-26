import signal
import asyncio


async def wait():
    "Await in the main task to wait for a SIGINT or SIGTERM"
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, stop_event.set)
    loop.add_signal_handler(signal.SIGINT, stop_event.set)
    await stop_event.wait()
