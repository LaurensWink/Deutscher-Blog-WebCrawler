from loguru import logger
from models.sql_models import Author, Blog, Post, Tag
from database.SQ_db import engine
from sqlmodel import Session, select

def get_db_stats() -> None: 
    with Session(engine) as session:
        statement = select(Tag).where(Tag.processed == True)
        all_processed_tags = session.exec(statement).all()
        logger.info(f'Das Programm hat: {len(all_processed_tags)} Tags überprüft.')
        statement = select(Post.ID)
        all_posts = session.exec(statement).all()
        logger.info(f'Es wurden insgesammt: {len(all_posts)} unique Posts gefunden.')
        statement = select(Blog.site_ID)
        all_blogs = session.exec(statement).all()
        logger.info(f'Diese wurden in: {len(all_blogs)} uniquen Blogs veröffentlicht.')
        statement = select(Post.ID, Post.language).where(Post.language == 'de')
        all_german_posts = session.exec(statement).all()
        logger.info(f'Als deutsch erkannt, wurden: {len(all_german_posts)} Posts.')
        statement = select(Author.ID)
        all_authors = session.exec(statement).all()
        logger.info(f'Zu den Posts sind: {len(all_authors)} unique Authoren gefunden worden (nicht für alle Posts sind Authoren bekannt).')


def get_all_blogs() -> list[Blog]:
    '''Returns all Blogs'''
    with Session(engine) as session:
        statement = select(Blog)
        return session.exec(statement).all()

def get_all_tags() -> list[Tag]:
    '''Returns all Tags'''
    with Session(engine) as session:
        statement = select(Tag)
        return session.exec(statement).all()
    
def get_all_authors() -> list[Author]:
    '''Returns all Authors'''
    with Session(engine) as session:
        statement = select(Author)
        return session.exec(statement).all()
 
def get_posts_by_blog(blog: Blog) -> list[Post]:
    '''Returns all posts published under given blog'''
    with Session(engine) as session:
        statement = select(Blog).where(Blog.site_ID == blog.site_ID)
        blog_session = session.exec(statement).first()
        return blog_session.posts if blog_session else []


def get_posts_by_tag(tag: Tag) -> list[Post]:
    '''Returns all posts published under given tag'''
    with Session(engine) as session:
        statement = select(Tag).where(Tag.name == tag.name)
        tag_session = session.exec(statement).first()
        return tag_session.posts if tag_session else []
    
def get_posts_by_author(author: Author) -> list[Post]:
    '''Returns all posts published by given Author'''
    with Session(engine) as session:
        statement = select(Author).where(Author.ID == author.ID)
        author_session = session.exec(statement).first()
        return author_session.posts if author_session else []