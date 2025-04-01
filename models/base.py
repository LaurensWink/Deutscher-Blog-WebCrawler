from __future__ import annotations
from bs4 import BeautifulSoup
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field
from api_functions.api_handler import API_Handler
from models.language import Language

class Base(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
    )

class Tag(Base):
    name: str

    def get_all_blog_posts(self) -> list['Post']: # type: ignore
        posts_by_tag: list[Post] = []
        response = API_Handler().get_all_blog_posts_by_tag(self.name)
        if response:
            for item in response:
                try:
                    # Bandaid fix for tags not being a list of Tag objects
                    item['tags'] = [{'name': tag}for tag in item['tags']]
                    posts_by_tag.append(Post(**item))
                except Exception as e:
                    logger.error(f'Error while instancing Post {e}')
        return posts_by_tag

class Blog(Base):
    site_id: int  = Field(alias='ID')
    blog_url: str = Field(alias='URL')
    name: str
    posts: list[Post]

class Post(Base):
    post_id: int = Field(alias='ID')
    site_id: int = Field(alias='site_ID')
    post_url: str = Field(alias='URL')
    author: Author | None = None
    language: Language | None = None
    content: str | None = None
    title: str | None = None
    tags: list[Tag]
    blog_text: str | None = None

    def get_full_post(self) -> Post:
        response = API_Handler().get_blog_post(self.post_id, self.site_id)

        if not response:
            return self
        
        content = response['content']
        title = response['title']

        soup = BeautifulSoup(content, 'html.parser')
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'a'])
        text_content = ' '.join([element.get_text() for element in text_elements])
        blog_text = title + ' ' + text_content

        return Post(
            post_id=self.post_id,
            site_id=self.site_id,
            post_url=self.post_url,
            author=self.author,
            language=None,
            title=title,
            content=content,
            tags=self.tags,
            blog_text=blog_text
        )

class Author(Base):
    author_id: int = Field(alias='ID')
    name: str
    profile_url: str|None = None