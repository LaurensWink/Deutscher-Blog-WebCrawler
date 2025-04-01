import os
from typing import Any, List, OrderedDict
from bs4 import BeautifulSoup
import httpx
from loguru import logger
import pandas as pd
from api_functions.api_handler import API_Handler
from utility.file_state_manager import File_State_Manager
import json
from langdetect import detect
from concurrent.futures import ThreadPoolExecutor
    
def get_initial_tags() -> list:
    df = pd.read_csv('data/csv/initial/tags.csv')
    tag_list = [url.rsplit('/', 1)[-1] for url in df['tags']]
    df_api = pd.read_csv('data/csv/initial/api_tags.csv')
    return list(OrderedDict.fromkeys(list(tag_list) + list(df_api['tags'])))    

def get_all_unique_blogs(iterations_directory: str = 'data/json/iterations') -> dict[str,List]:
    combined_blogs = {}
    unique_blogs = set()
    used_files = []

    if os.path.exists('data/json/iterations'):
                for file in os.listdir('data/json/iterations'):
                    if file.endswith('.json'):
                        used_files.append(file)
                        with open(os.path.join('data/json/iterations', file), encoding='utf-8') as jsonfile:
                            blog_data = json.load(jsonfile)
                            for tag, blogs in blog_data.items():
                                if tag not in combined_blogs:
                                    combined_blogs[tag] = []
                                combined_blogs[tag].extend(blogs)

    for blogs_list in combined_blogs.values():
        for post in blogs_list:
            unique_blogs.add(post['site_id'])
    
    return {'used_files': used_files, 'unique_blog_ids': list(unique_blogs)}

def posts_by_blog(unique_blog_ids: List) -> None:
     for id in unique_blog_ids[1:2]:
          response = api_handler.get_posts_by_blog(id)
          print(response["posts"][0]["author"])

api_handler = API_Handler()
file_state_manager = File_State_Manager()
posts_by_blog(get_all_unique_blogs()['unique_blog_ids'])