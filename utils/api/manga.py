# import requests
from typing import Union

from httpx import AsyncClient, Response

# colocar properties "relationships" e "attributes" para facilitar?
class Manga:
    BASE_URL = 'https://api.mangadex.org'
    BASE_UPLOADS_URL = 'https://uploads.mangadex.org'

    def __init__(self, id:str):
        self.id = id
        self._init_properties()

    def _init_properties(self):
        'Função para organizar a inicialização das properties, definindo todas as variáveis necessárias como None, evitando a poluição do init'
        self._manga_data = {}

        self._title = ''
        self._genres = []
        self._content_rating = ''
        self._translated_languages = []

        self._cover_id = ''
        self._cover_filename = ''
        self._cover_image = None
    
    async def get_manga_data(self) -> dict:
        if not self._manga_data:
            try:
                async with AsyncClient() as client:
                    response = await client.get(f'{self.BASE_URL}/manga/{self.id}')
                self._manga_data = response.json()['data']
            except Exception as e:
                print(f'Erro ao buscar os dados do mangá: {e}')
        return self._manga_data
    
    def set_manga_data(self, data:dict):
        self._manga_data = data
    
    async def get_title(self) -> str:
        if not self._title:
            try:
                self._title = (await self.get_manga_data())['attributes']['title']['en']
            except Exception as e:
                print(f'Erro ao obter título do mangá: {e}')
        return self._title

    async def get_content_rating(self) -> str: # "safe" | "suggestive" | "erotica" | "pornographic"
        if not self._content_rating:
            try:
                self._content_rating = (await self.get_manga_data())['attributes']['contentRating']
            except Exception as e:
                print(f'Erro ao obter a classificação do conteúdo: {e}')
        return self._content_rating

    async def get_genres(self) -> list[str]:
        if not self._genres:
            try:
                tags = (await self.get_manga_data())['attributes']['tags']
                for tag in tags:
                    if tag['attributes']['group'] == 'genre':
                        self._genres.append(tag['attributes']['name']['en'])
                        # retorna apenas os generos em ingles, mudar isso depois?
            except Exception as e:
                print(f'Erro ao obter os gêneros do mangá: {e}')
        return self._genres

    async def get_translated_languages(self) -> list[str]:
        if not self._translated_languages:
            try:
                self._translated_languages = (await self.get_manga_data())['attributes']['availableTranslatedLanguages']
            except Exception as e:
                print(f'Erro ao obter os idiomas disponíveis: {e}')
        return self._translated_languages

    async def get_cover_id(self) -> str:
        if not self._cover_id:
            try:
                # vai pegar a primeira cover art que encontrar, tem alguma cover que seja melhor que outra?
                for relation in (await self.get_manga_data())['relationships']: 
                    if relation['type'] == 'cover_art':
                        self._cover_id = relation['id']
                        break
                if not self._cover_id:
                    raise Exception('id não encontrado nos relacionamentos')
            except Exception as e:
                print(f'Erro ao buscar id da cover: {e}')
        return self._cover_id

    async def get_cover_filename(self) -> str:
        if not self._cover_filename:
            try:
                async with AsyncClient() as client:
                    response = await client.get(f'{self.BASE_URL}/cover/{await self.get_cover_id()}')
                self._cover_filename = response.json()['data']['attributes']['fileName']
            except Exception as e:
                print(f'Erro ao buscar o filename da cover: {e}')
        return self._cover_filename
    
    async def get_cover_image(self) -> Union[Response, None]:
        if not self._cover_image:
            try:
                async with AsyncClient() as client:
                   self._cover_image = await client.get(f'{self.BASE_UPLOADS_URL}/covers/{self.id}/{await self.get_cover_filename()}')
                # self._cover_image = response.content
            except Exception as e:
                print(f'Erro ao buscar a imagem da cover_art: {e}')
        return self._cover_image 
    
if __name__ == '__main__':
    jojo = Manga('1044287a-73df-48d0-b0b2-5327f32dd651')