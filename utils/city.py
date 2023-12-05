import aiohttp

url = "https"

async def check(name: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get() as response:
            if response.
