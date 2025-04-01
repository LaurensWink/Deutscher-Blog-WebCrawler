from loguru import logger
from web_crawler.web_crawler import Web_Crawler

from utility.constant_variables import TAG_PAGE, WORD_PRESSS_PREFIX

###Tags containing ä,ü,ö or ß are currently not functional, but i dont filter them out just in case they are getting fixed in the future###

web_crawler = Web_Crawler()

tag_list = web_crawler.get_tags(TAG_PAGE, WORD_PRESSS_PREFIX)

logger.info(f'Taglist: {tag_list}') 