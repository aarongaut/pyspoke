import asyncio

ExpectedConnectErrors = ConnectionRefusedError
ExpectedReadErrors = (
    asyncio.exceptions.IncompleteReadError,
    BrokenPipeError,
    ConnectionResetError,
)
ExpectedWriteErrors = BrokenPipeError, ConnectionResetError
