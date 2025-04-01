import json
import os
from typing import Any, List
from loguru import logger
import pandas as pd
from pathvalidate import sanitize_filename 
from models.base import Post, Tag


def write_to_csv(tag_list: List[str], directory: str, name: str) -> None:
    df = pd.DataFrame(tag_list, columns=["tags"])
    name = sanitize_filename(name)
    data_name = f'data/csv/{directory}/{name}.csv'
    df.to_csv(data_name)
    logger.info(f'Succesfully created {data_name}')

def write_to_json(dictionary: dict[str, Any], directory: str, name: str) -> None:
    name = sanitize_filename(name)
    data_name = f'data/json/{directory}/{name}.json'
    with open(data_name, "w") as outfile: 
        json.dump(dictionary, outfile)
    logger.info(f'Succesfully created {data_name}')

def delete_all_files(directory: str) -> None:
    if not os.path.exists(directory):
        logger.warning(f'Directory {directory} does not exist')
        return
    
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            logger.info(f'deleted: {file_path}')

def create_new_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def dump_tag_list(tag_list: list[Tag]) -> list[str]:
    return [tag.name for tag in tag_list]

def dump_blogs_by_tag(blogs_by_tag: dict[str, Post]) -> dict[str, Any]:
    return {tag: [post.model_dump() for post in posts] for tag, posts in blogs_by_tag.items()}