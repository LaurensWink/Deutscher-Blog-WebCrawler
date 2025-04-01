import httpcore
from typing import Any
import httpx
from loguru import logger

from models.sql_models import Author, Blog, Post, Tag

class API_Handler():
    #For dokumentation see: https://developer.wordpress.com/docs/api/ and https://public-api.wordpress.com/wpcom/v2

    URL_PREFIX = 'https://public-api.wordpress.com/'

    async def get_all_tags(self) -> list[Tag] | None:
        url = f'{self.URL_PREFIX}rest/v1.2/read/tags/alphabetic'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.ReadTimeout, httpcore.ReadError, httpx.ConnectTimeout) as e:
            logger.error(f'HTTP error occurred: {e}')
            return None

        return self.__return_as_tag_list(response.json())

    async def get_blog_post(self, post_id: int, site_id: int, field_array: list = ['ID','site_ID','URL','author','tags','title','content']) -> Post | None:
        fields: str = ','.join(field_array)
        url = f'{self.URL_PREFIX}rest/v1.1/sites/{site_id}/posts/{post_id}?fields={fields}'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.ReadTimeout, httpcore.ReadError, httpx.ConnectTimeout) as e:
            logger.error(f'HTTP error occurred: {e}')
            return None
        
        return await self.__return_as_post_tupel(response.json())

    async def get_blog(self, site_id: int) -> dict[str, Any] | None:
        url = f'{self.URL_PREFIX}rest/v1.1/sites/{site_id}'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.ReadTimeout, httpcore.ReadError, httpx.ConnectTimeout) as e:
            logger.error(f'HTTP error occurred: {e}')
            return None
        
        return self.__return_as_blog(response.json())

    async def __get_blogs_by_tag(self, tag: str, field_array: list, page: int = 1, per_page: int = 10) -> dict[str, Any] | None:
        fields: str = ','.join(field_array)
        url = f'{self.URL_PREFIX}wpcom/v2/read/tags/{tag}/posts?page={page}&number={per_page}&_locale=de&fields={fields}'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.ReadTimeout, httpcore.ReadError, httpx.ConnectTimeout) as e:
            logger.error(f'HTTP error occurred: {e}')
            return None

        return response.json()
    
    async def get_all_blog_posts_by_tag(self, tag: str, field_array: list = ['ID','site_ID','URL','author','tags','title','content']) -> list[tuple[Post,Author,list[Tag]]]:
        all_blogs = []
        page = 1
        per_page = 40

        while True:
            blogs = await self.__get_blogs_by_tag(tag, field_array, page, per_page)
            if not blogs:
                break
            elif len(blogs['posts']) == 0:
                break

            all_blogs.extend(blogs['posts'])
            page += 1

        logger.info(f'Searching for tag: {tag}')
        logger.info(f'Total blogs collected for {tag}: {len(all_blogs)}')
        return [await self.__return_as_post_tupel(post) for post in all_blogs]

    async def get_posts_by_blog(self, site_id: int)-> dict[str, Any] | None:
        url = f'{self.URL_PREFIX}rest/v1.1/sites/{site_id}/posts/'
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
            response.raise_for_status()
        except (httpx.HTTPStatusError, httpx.ReadTimeout, httpcore.ReadError, httpx.ConnectTimeout) as e:
            logger.error(f'HTTP error occurred: {e}')
            return None

        return [await self.__return_as_post_tupel(post) for post in response.json()['posts']]
    
    async def __return_as_post_tupel(self, post_data: dict[str, Any]) -> tuple[Post,Author,list[Tag]]|None:
        author: Author | None = None
        if post_data.get('author'):
            author = Author.model_validate(Author(**post_data['author']))
        tag_list: list[Tag] = [Tag.model_validate(Tag(name = tag))for tag in post_data['tags']]
        post: Post = Post(
            site_ID=post_data['site_ID'],
            ID=post_data['ID'],
            URL=post_data['URL'],
            language=None,
            content=post_data['content'],
            title=post_data['title'],
            author_id= author.ID if author else None,
            )
        post.tags = tag_list
        await post.detect_language()
        post = Post.model_validate(post)
        return post, author, tag_list
    
    def __return_as_tag_list(self, tag_data: dict[str, Any]) -> list[Tag]:
        all_tags: list[Tag] = []
        
        for tag_list in dict(tag_data).values():
            for tag in tag_list:
                all_tags.append(Tag.model_validate(Tag(name = tag['display_name'])))
        
        return all_tags
    
    def __return_as_blog(self, blog_data: dict[str, Any]) -> Blog:
        return Blog.model_validate(
            Blog(
            site_ID =blog_data['ID'],
            name = blog_data['name'],
            description = blog_data['description'],
            URL = blog_data['URL'],
            access= True
            )
        )