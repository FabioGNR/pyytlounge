from aiohttp import StreamReader


async def as_aiter(iterator):
    """Turns a synchronous iterator into an asynchronous iterator"""
    for item in iterator:
        yield item


async def iter_response_lines(resp: StreamReader):
    """Enumerate lines in response one at a time."""
    while True:
        line = await resp.readline()
        if line:
            yield line.decode()
        else:
            break
