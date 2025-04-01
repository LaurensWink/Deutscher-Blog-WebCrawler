from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
from threading import Lock
from typing import Tuple
from loguru import logger
from pathvalidate import sanitize_filename
from models.language import Language
from models.base import Post, Tag
from langdetect import detect

from utility.file_state_manager import create_new_folder, delete_all_files, dump_blogs_by_tag, write_to_json


class Iteration(): 
    def __init__(self, initial_tags: list[Tag], initial_blogs_by_tag: dict[str, list[Post]], number: int):
        self.initial_tags: list[Tag] = initial_tags
        self.initial_blogs_by_tag: dict[str, list[Post]] = initial_blogs_by_tag
        self.iteration_tag_list: list[Tag] = []
        self.blogs_by_tag_german: dict[str, list[Post]] = {}
        self._lock = Lock()
        self.number = number
        self.path = Path(f'data/json/iterations/iteration_{self.number}')
        
        self._iterate()

#NOTE: Tags may differ even on the same Data, because langdetect is not deterministic

    def _iterate(self) -> None:
        with self._lock:
            self.path.mkdir(parents=True, exist_ok=True)
        for tag in self.initial_blogs_by_tag:
            german_posts = self._filter_german_posts(self.initial_blogs_by_tag[tag])
            
            with self._lock:
                if german_posts:
                    (self.path/f'{sanitize_filename(tag)}_store.json').write_text(json.dumps(dump_blogs_by_tag({tag: german_posts})))
                
        self._process_all_german_blogs()

    def _process_all_german_blogs(self) -> None:

        for filename in self.path.iterdir():
            if filename.suffix == ".json":
                data = json.loads(filename.read_text(encoding="utf-8"))

                new_tags = self._get_new_tag_list((self.initial_tags + self.iteration_tag_list), [Post(**post) for post in next(iter(data.values()))])  
            
                with self._lock:
                    self.iteration_tag_list.extend(new_tags)

    def _get_new_tag_list(self, current_tags: list[Tag], posts: list[Post]) -> list[Tag]:
        current_tags_set: set[Tag] = set(current_tags)
        total_post_tags: set[Tag] = set()
        for post in posts:
            for tag in post.tags:
                total_post_tags.add(tag)
        
        return list(total_post_tags.difference(current_tags_set))

    def _filter_german_posts(self, posts: list[Post], num_threads: int = 8) -> Tuple[list[Post], list[Post]]:
        german_posts: list[Post] = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_post = {executor.submit(post.get_full_post): post for post in posts}

            for future in as_completed(future_to_post):
                full_post = future.result()

                if not full_post.blog_text:
                    continue

                try: 
                    dump = full_post.model_dump()
                    dump['language'] = detect(full_post.blog_text)
                    post_with_lang = Post(**dump)

                    if post_with_lang.language == Language.de:
                        german_posts.append(post_with_lang)
                except Exception as e:
                    logger.error(f'No text to analyse: {e}')

                

        return german_posts
