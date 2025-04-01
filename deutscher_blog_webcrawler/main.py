from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from loguru import logger
import pandas as pd
from api_functions.api_handler import API_Handler
from api_functions.iteration import Iteration
from models.base import Post, Tag
from utility.constant_variables import TAG_PAGE 
from utility.file_state_manager import write_to_csv, write_to_json, dump_blogs_by_tag, dump_tag_list
from web_crawler.web_crawler import Web_Crawler

api_handler = API_Handler()
web_crawler = Web_Crawler()

def init_tags() -> list[Tag]:
    logger.info(f'Fetching for initial Tag-List')
    tag_list: list[Tag] = []

    for tags_by_alphabetical_order in api_handler.get_all_tags().values():
        for tag in tags_by_alphabetical_order:
            tag_list.append(Tag(name=tag['display_name']))


    for tag_name in web_crawler.get_tags(TAG_PAGE):
        tag_list.append(Tag(name=tag_name))
    
    return tag_list

def get_blog_posts_by_tag_list(tags: list[Tag], num_threads: int = 8) -> dict[str, list[Post]]:
    all_blog_posts_by_tag_list = {}

    logger.info(f'Processing {len(tags)} tags with {num_threads} threads.')

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_tag = {executor.submit(tag.get_all_blog_posts): tag for tag in tags}

        for future in as_completed(future_to_tag):
            tag = future_to_tag[future]
            try:
                blog_posts = future.result()
                all_blog_posts_by_tag_list[tag.name] = blog_posts
            except Exception as e:
                logger.error(f"Error processing tag {tag.name}: {e}")
                all_blog_posts_by_tag_list[tag.name] = []

    return all_blog_posts_by_tag_list

def read_all_iteration_tags(directory: str = 'data/csv/iterations') -> list[Tag]:
    if not os.path.exists(directory):
        logger.error(f"Directory '{directory}' does not exist.")

    iteration_tags: list[Tag] = []
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            file_path = os.path.join(directory, file)
            try:
                iteration_tags = iteration_tags + [Tag(name = tag) for tag in pd.read_csv(file_path)['tags']]
            except Exception as e:
                logger.error(f"Error while loading file {file}: {e}")
    
    return iteration_tags

def run_iterations(amount: int, initial_tags: list[Tag], initial_blogs_by_tag: dict[str, list[Post]]) -> None:
    current_blogs_by_tag = initial_blogs_by_tag
    for iteration_count in range(amount):
        total_tags: list[Tag] = initial_tags + read_all_iteration_tags()
        iteration = Iteration(total_tags, current_blogs_by_tag, iteration_count)
        write_to_csv(dump_tag_list(iteration.iteration_tag_list), 'iterations', f'iteration_{iteration_count}')
        tag_list: list[Tag] = iteration.iteration_tag_list
        del iteration
        current_blogs_by_tag = get_blog_posts_by_tag_list(tag_list)


def main() -> None:
    
    tag_list: list[Tag] = init_tags()
    write_to_csv(dump_tag_list(tag_list), 'initial', 'tags')
    
    tag_list: list[Tag] = [Tag(name = tag) for tag in pd.read_csv('data/csv/initial/tags.csv')['tags']]

    blogs_by_tag: dict[str, list[Post]] = get_blog_posts_by_tag_list(tag_list)

    write_to_json(dump_blogs_by_tag(blogs_by_tag), 'initial', 'blog_posts')

    with open('data/json/initial/blog_posts.json') as file:
        blogs_by_tag_json = json.load(file)

    blogs_by_tag: dict[str, list[Post]] = {
        tag: [Post(**post) for post in posts] 
        for tag, posts in blogs_by_tag_json.items()
    }

    run_iterations(10, tag_list, blogs_by_tag)
    

main()