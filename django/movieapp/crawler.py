import requests
import re
from enum import Enum
import logging

logger = logging.getLogger('debug')

class LinkType(Enum):
        IMDB = 0
        TMDB = 1

class Crawler:

    def __init__(self, link_id, movie_title, link_type: LinkType):
        self.__link_id__ = link_id
        self.__url__ = "https://www.imdb.com/title/tt0{0}/".format(link_id) if link_type == LinkType.IMDB else "" 
        self.__html_text__ = self.__get_html_content()

    def __get_html_content(self):
        try:
            ret = requests.get(self.__url__)
            html_text = ret.text
            return html_text
        except Exception:
            logger.info()
            return ""

    def __bool__(self):
        return self.__html_text__ != ""

    def get_imdb_img_url(self) -> str:
        reg_src = r"title=\"[\w\s]+\"\ssrc=\"[\S]+\""
        reg_url = r"http[^\"]+"

        # get html
        html_text = self.__html_text__

        matched_patterns = re.findall(reg_src, html_text)
        matched_pattern = matched_patterns[0] if len(matched_patterns)>0 else None
        matched_url = re.findall(reg_url, matched_pattern)[0] if matched_pattern else None
        
        return matched_url if matched_url else None
    
    def get_summary_context(self) -> str:
        logger.info("here")
        reg_tag = r"<div class=\"summary_text\">"
        logger.info(reg_tag)
        # reg_url = r"http[^\"]+"

        # get html
        html_text = self.__html_text__

        matched_patterns = re.findall(reg_tag, html_text)
        logger.info(str(matched_patterns))
        matched_pattern = matched_patterns[0] if len(matched_patterns)>0 else None
        # matched_url = re.findall(reg_url, matched_pattern)[0] if matched_pattern else None
        
        return matched_pattern if matched_pattern else None