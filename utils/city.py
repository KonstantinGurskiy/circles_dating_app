import aiohttp

url = "https://nominatim.openstreetmap.org/search?format=json&q="

async def check(name: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{utl}{name}") as response:
            if response.status = 200:
                return = True
    return False
