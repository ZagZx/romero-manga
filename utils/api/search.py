from httpx import AsyncClient

BASE_URL = 'https://api.mangadex.org'

async def search_manga_by_title(title:str) -> list[dict]:
    try:
        async with AsyncClient() as client:
            response = await client.get(f'{BASE_URL}/manga?title={title}')
            return response.json()['data']
    except Exception as e:
        print(f'Erro ao pesquisar mangás: {e}')
        return []
