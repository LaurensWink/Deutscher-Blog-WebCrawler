import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from utility.file_state_manager import write_to_csv
from utility.constant_variables import COUNTER_CLASS_TAG_PAGE

def validate_tag(tag_url:str, counter_class:str):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(tag_url)

    try:
        #Wait until at least one Element is loaded or 5s went by
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, counter_class))
        )
    except Exception as e:
        logger.error(f"Timeout while loading site: {e}")
        driver.quit()
        return False
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    count_text = soup.find("span", class_= counter_class).get_text(strip=True)
    count = int(count_text.replace('.', '').replace(',', ''))  

    if count > 0:
        driver.quit()
        return True
    else:
        driver.quit()
        return False



def creat_valid_tags_csv(path:str, link_class:str):
    df = pd.read_csv(path)
    tag_list = df["tags"]
    tag_list = tag_list[tag_list.apply(lambda tag: validate_tag(tag, link_class))]
    
    write_to_csv(tag_list, "initial/valid_tags")



creat_valid_tags_csv("data/csv/initial/tags.csv", COUNTER_CLASS_TAG_PAGE)