import requests
import re

def get_imdb_img(imdbId, movie_title):
    url = "https://www.imdb.com/title/tt0{0}/".format(imdbId)

    reg_src = r"title=\"[\w\s]+\"\ssrc=\"[\S]+\""
    reg_url = r"http[^\"]+"
    # get response
    ret = requests.get(url)
    # get html
    html_text = ret.text

    matched_patterns = re.findall(reg_src, html_text)
    matched_pattern = matched_patterns[0] if len(matched_patterns)>0 else None
    matched_url = re.findall(reg_url, matched_pattern)[0] if matched_pattern else None
    
    return matched_url if matched_url else None