import asyncio

from alive_progress import alive_it
from loguru import logger
from sqlalchemy import insert
from api_functions.api_handler import API_Handler
from database.SQ_db import create_db_and_tables, engine
from sqlmodel import Session, select
from models.sql_models import Author, Blog, Post, Post_Tag, Tag
from sqlalchemy import distinct


async def fetch_initial_tags() -> None:
    with Session(engine) as session:
        tag_list: list[Tag] = await API_Handler().get_all_tags()
        for tag in alive_it(tag_list):
            session.exec(
                insert(Tag).values(
                    name=tag.name
                ).prefix_with("OR IGNORE")
            )
        session.commit()


def write_response_tupel(response_tupel_list: list[tuple[Post, Author, list[Tag]]]|None, session: Session) -> None:
    for post_tuple in alive_it(response_tupel_list):
        post, author, tag_list = post_tuple

        if author:
            session.exec(
                insert(Author).values(
                    ID=author.ID,
                    name=author.name,
                    profile_URL=author.profile_URL
                ).prefix_with("OR IGNORE")
            )

            session.exec(
                insert(Post).values(
                    ID=post.ID,
                    site_ID=post.site_ID,
                    URL = post.URL,
                    language= post.language,
                    content= post.content,
                    title= post.title,
                    author_id = post.author_id 
                ).prefix_with("OR IGNORE")
            )

            for tag in tag_list:
                session.exec(
                    insert(Tag).values(
                        name=tag.name
                    ).prefix_with("OR IGNORE")
                )
               
                session.exec(
                    insert(Post_Tag).values(
                        site_id = post.site_ID,
                        post_id = post.ID,
                        tag_name = tag.name
                    ).prefix_with("OR IGNORE")
                )

async def iterate_unprocessed_tags() -> None:
    with Session(engine) as session:
        unprocessed_tags: list[Tag] = session.exec(select(Tag).where(Tag.processed == False)).fetchall()
        
        for unprocessed_tag in unprocessed_tags:
            logger.info(f'Processing {unprocessed_tag.name}')
            post_tuple_list: list[tuple[Post, Author, list[Tag]]]|None = await API_Handler().get_all_blog_posts_by_tag(tag=unprocessed_tag.name)

            if post_tuple_list:
                write_response_tupel(post_tuple_list, session)

            unprocessed_tag.processed = True
            session.commit()
            logger.info(f'Processing of {unprocessed_tag.name} complete')

async def iterate_unique_siteIDs() -> None:
    with Session(engine) as session:
        unique_site_IDs = session.exec(select(distinct(Post.site_ID))).all()
        for site_ID in unique_site_IDs:
            post_tuple_list: list[tuple[Post, Author, list[Tag]]]|None = await API_Handler().get_posts_by_blog(site_ID)
            if post_tuple_list:
                write_response_tupel(post_tuple_list, session)
            blog: Blog = await API_Handler().get_blog(site_ID)
            if blog:
                session.exec(
                    insert(Blog).values(
                        site_ID = blog.site_ID,
                        name = blog.name,
                        description = blog.description,
                        URL = blog.URL,
                        access = blog.access
                    ).prefix_with("OR IGNORE")
                )
            else:
                session.exec(
                    insert(Blog).values(
                        site_ID = site_ID,
                        name = None,
                        description = None,
                        URL = None,
                        access = False
                    ).prefix_with("OR IGNORE")
                )
            session.commit()

def validate_licences() -> None:
    with Session(engine) as session:
        statement = select(Blog)
        all_blogs = session.exec(statement).all()
        for blog in all_blogs:
            blog.cc_licence = blog.validate_licence() 
            session.commit()
        logger.info("Exit validate function")

if __name__ == "__main__":
    ITERATIONS: int = 50
    create_db_and_tables()
    asyncio.run(fetch_initial_tags())
    for count in range(ITERATIONS):
        asyncio.run(iterate_unprocessed_tags())
    asyncio.run(iterate_unique_siteIDs())
    validate_licences()