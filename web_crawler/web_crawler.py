import time
from typing import Any, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from loguru import logger

class Web_Crawler():
    TAG_URL_PREFIX  = 'https://wordpress.com/de/tag/'

    def get_tags(self, url: str):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        link_elements = soup.select("a[href]")
        tag_urls = [a["href"] for a in link_elements if "de/tag/" in a["href"]]
        tag_list = [url.rsplit('/', 1)[-1] for url in tag_urls]
        return tag_list

    def __get_blogs_by_tag(self, tag:str, link_class:str, scrolls:int, last_loaded:str=None) -> List:
    ###Collects all Blog-Urls for a given Tag. link_class is the css class of the Blog-link and last_loaded should be the css class of the last loaded element###
    
        #If no last_loaded given last_loaded should equal link_class
        if not last_loaded:
            last_loaded = link_class

        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        blog_urls = []
        tag_url = self.TAG_URL_PREFIX + tag

        driver.get(tag_url)

        try:
            #Wait until at last_loaded Element is loaded or 5s went by
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, last_loaded))
            )
        except Exception as e:
            logger.error(f'Timeout while loading Site: {e}')
            driver.quit()
            return []
        
        for _ in range(scrolls):
            try:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(5)
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                link_tags = soup.find_all('a', class_=link_class)
                link_list = [link.get('href') for link in link_tags]

                if len(blog_urls) > 0 and len(link_list) > 0:
                    if blog_urls[-1] == link_list[-1]:
                        driver.quit()
                        return set(blog_urls)
                elif not len(link_list) > 0:
                    driver.quit()
                    return set() 
                
                blog_urls = blog_urls + link_list
                
            except Exception as e:
                logger.error(f'Collecting Site-data failed: {e}')
                driver.quit()
                return set() 

        driver.quit()
        return list(set(blog_urls))
    
    def get_blogs_by_tag_list(self, tag_list: List[str], link_class: str, last_loaded: str, max_scrolls: int) -> dict[str, list[Any]]:
        blogs_by_tag = {}

        for tag in tag_list:
            blogs_by_tag[tag] = list(self.__get_blogs_by_tag(tag, link_class, max_scrolls, last_loaded))
            logger.info(f'Collected posts for: {tag}')

        return blogs_by_tag