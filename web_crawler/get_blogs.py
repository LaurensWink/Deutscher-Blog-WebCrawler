from typing import Any, List
from loguru import logger
import pandas as pd
from web_crawler.web_crawler import Web_Crawler
from utility.constant_variables import LINK_CLASS_TAG_PAGE, LAST_LOADED_ELEMENT_TAG_PAGE
    
def fetch_posts(max_scrolls: int, tags_path: str) -> dict[str,List[Any]]:
    web_crawler = Web_Crawler()
    df = pd.read_csv(tags_path)
    tag_list = df["tags"]
    logger.info(f'Loaded Tags: {tag_list}')
    blogs_posts_by_tag_list = web_crawler.get_blogs_by_tag_list(
        tag_list=tag_list, 
        link_class=LINK_CLASS_TAG_PAGE, 
        last_loaded=LAST_LOADED_ELEMENT_TAG_PAGE,
        max_scrolls=max_scrolls
        )
    return blogs_posts_by_tag_list
    
fetch_posts(250,'data/csv/initial/tags.csv')