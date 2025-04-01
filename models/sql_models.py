from typing import List, Optional
from bs4 import BeautifulSoup
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import BigInteger, ForeignKeyConstraint
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from models.language import Language

DetectorFactory.seed = 0

def detect_language(text: str):
    try:
        return Language(detect(text))
    except LangDetectException:
        return "unknown"

class Post_Tag(SQLModel, table=True):
    site_id: int = Field(
        primary_key=True,
        sa_type=BigInteger,
    )
    post_id: int = Field(
        primary_key=True,
        sa_type=BigInteger,
    )
    tag_name: str = Field(
        foreign_key='tag.name',
        primary_key=True,
    )
    __table_args__ = (
        ForeignKeyConstraint(
            ['site_id', 'post_id'],
            ['post.site_ID', 'post.ID'],
        ),
    )

class Tag(SQLModel, table=True):
    name: str = Field(primary_key=True)
    processed: bool = Field(default=False)

    posts: list['Post'] = Relationship(back_populates='tags', link_model=Post_Tag)

class Post(SQLModel, table=True):
    ID: int = Field(primary_key=True, sa_type=BigInteger)
    site_ID: int = Field(primary_key=True, foreign_key="blog.site_ID", sa_type=BigInteger)
    URL: str
    language: str | None = None
    content: str
    title: str

    author_id: int | None = Field(default=None, foreign_key='author.ID')

    author: Optional['Author'] = Relationship(back_populates='posts')
    tags: List[Tag] = Relationship(back_populates='posts', link_model=Post_Tag)
    blog: 'Blog' = Relationship(back_populates='posts')

    def text(self) -> str:
        soup = BeautifulSoup(self.content, 'html.parser')
        return soup.get_text()
    
    async def detect_language(self) -> Language | None:
        text = f'{self.title}\n\n{self.text()}'
        lang = detect_language(text)
        if lang and lang != 'unknown':
            self.language = lang.name
        return lang

class Author(SQLModel, table=True):
    ID: int = Field(primary_key=True, sa_type=BigInteger)
    name: str
    profile_URL: str | None = None

    posts: list[Post] = Relationship(back_populates='author')

class Blog(SQLModel, table=True):
    site_ID: int = Field(primary_key=True, sa_type=BigInteger)
    name: str|None
    description: str|None
    URL: str|None
    access: bool
    posts: list[Post] = Relationship(back_populates="blog")
    cc_licence: bool = Field(default=False)

    def validate_licence(self) -> bool:
        cc_links: list[str] = []
        for post in self.posts:
            soup = BeautifulSoup(post.content, 'html.parser')
            cc_links = [a["href"] for a in soup.find_all("a", href=True) if "creativecommons.org" in a["href"]]

        if cc_links:
            return True
        else: return False