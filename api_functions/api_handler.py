from typing import Any
import httpx
from loguru import logger

class API_Handler():
    #For dokumentation see: https://developer.wordpress.com/docs/api/ and https://public-api.wordpress.com/wpcom/v2

    URL_PREFIX = 'https://public-api.wordpress.com/'


    def get_all_tags(self) -> dict[str, Any] | None:
        url = f'{self.URL_PREFIX}rest/v1.2/read/tags/alphabetic'
        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
        except Exception as e:
            logger.error(f'HTTP error occurred: {e}')
            return None

        return response.json()

    def get_blog_post(self, post_id: int, site_id: int) -> dict[str, Any] | None:
        url = f'{self.URL_PREFIX}rest/v1.1/sites/{site_id}/posts/{post_id}?fields=ID,site_ID,URL,author,tags,content,title,tags'
        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
        except Exception as e:
            logger.error(f'HTTP error occurred: {e}')
            return None
        
        return response.json()

    def get_blog(self, site_id: int) -> dict[str, Any] | None:
        url = f'{self.URL_PREFIX}rest/v1.1/sites/{site_id}'
        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
        except Exception as e:
            logger.error(f'HTTP error occurred: {e}')
            return None
        
        return response.json()

    def __get_blogs_by_tag(self, tag: str, page: int = 1, per_page: int = 10) -> dict[str, Any] | None:
        url = f'{self.URL_PREFIX}wpcom/v2/read/tags/{tag}/posts?page={page}&number={per_page}&_locale=de&fields=ID,site_ID,URL,author,tags'
        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
        except Exception as e:
            logger.error(f'HTTP error occurred: {e}')
            return None

        return response.json()
    
    def get_all_blog_posts_by_tag(self, tag: str) -> list:
        all_blogs = []
        page = 1
        per_page = 40

        while True:
            blogs = self.__get_blogs_by_tag(tag, page, per_page)
            if not blogs:
                break
            elif len(blogs['posts']) == 0:
                break

            all_blogs.extend(blogs['posts'])
            page += 1

        logger.info(f'Searching for tag: {tag}')
        logger.info(f'Total blogs collected for {tag}: {len(all_blogs)}')
        return all_blogs

    def get_posts_by_blog(self, site_id: int)-> dict[str, Any] | None:
        url = f'{self.URL_PREFIX}rest/v1.1/sites/{site_id}/posts/'
        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
        except Exception as e:
            logger.error(f'HTTP error occurred: {e}')
            return None

        return response.json()