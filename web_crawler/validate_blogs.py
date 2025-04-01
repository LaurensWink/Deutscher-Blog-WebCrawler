import json
from bs4 import BeautifulSoup
from langdetect import detect
from loguru import logger
import requests
from utility.file_state_manager import write_to_csv

def validate_blogs(path: str):
    valid_blogs = []
    
    with open(path, "r", encoding="utf-8") as file:
        blogs_dict = json.load(file)
        
    for tag_set in blogs_dict.values():   
        for blog in tag_set:
            response = requests.get(blog)

            if response.status_code != 200:
                logger.error(f"Fehler beim Abrufen der Seite: {response.status_code}")
                exit()

            soup = BeautifulSoup(response.content, "html.parser")

            link_elements = soup.select("a[href]")
            cc_links = [a["href"] for a in link_elements if "creativecommons" in a["href"]]
            
            if len(cc_links) > 0:
                valid_blogs.append(blog)
                logger.info(f'{blog}: cc')
            else: logger.info(f'{blog}: other license')
     
    write_to_csv(valid_blogs, "initial/valid_blogs")
    logger.info(valid_blogs)       

validate_blogs("data/json/initial/blogs_by_tag.json")