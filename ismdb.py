from bs4 import BeautifulSoup
import urllib
import os

import time
import string

from tqdm import tqdm
from utilities import format_filename, get_soup

ALL_URL = "https://www.imsdb.com/all%20scripts"
BASE_URL = "https://www.imsdb.com"
DIR = os.path.join("scripts", "ismdb")


def get_script_from_url(script_url):
    if not script_url.endswith('.html'):
        return ""

    script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
    if len(script_soup.find_all('td', class_="scrtext")) < 1:
        return ""
    script_text = script_soup.find_all('td', class_="scrtext")[0].pre

    text = ""
    if script_text:
        script_text = script_soup.find_all('td', class_="scrtext")[0].pre.pre
        if script_text:
            text = script_text.get_text()

        else:
            script_text = script_soup.find_all('td', class_="scrtext")[0].pre
            text = script_text.get_text()

    return text

def get_script_url(movie):
    script_page_url = movie.contents[0].get('href')
    movie_name = script_page_url.split("/")[-1].strip('Script.html')

    script_page_soup = get_soup(BASE_URL + urllib.parse.quote(script_page_url))
    paras = script_page_soup.find_all('p', align="center")
    if len(paras) < 1:
        return ""
    script_url = paras[0].contents[0].get('href')

    return script_url


soup = get_soup(ALL_URL)
movielist = soup.find_all('p')

for movie in tqdm(movielist[:10]):
    script_url = get_script_url(movie)
    if script_url == "":
        continue

    name = script_url.split("/")[-1].split('.html')[0]

    text = get_script_from_url(script_url)

    if text == "":
        continue

    name = format_filename(name)

    with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
        out.write(text)

    # print(name)



