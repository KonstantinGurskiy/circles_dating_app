import requests



async def get_place(api_key: str, lat: float, lon: float):
    url = f'https://api.opencagedata.com/geocode/v1/json?key={api_key}&q={str(lat)}+{str(lon)}&pretty=1'
    response = requests.get(url)
    data = response.json()

    if data['results']:
        location = data['results'][0]['formatted']
        return location
    else:
        return 'Название места не найдено'


