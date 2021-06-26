from bs4 import BeautifulSoup
import urllib
import os

import time
import string

from tqdm import tqdm
from .utilities import format_filename, get_soup, get_pdf_text


def get_imsdb():
    ALL_URL = "https://imsdb.com/all-scripts.html"
    BASE_URL = "https://imsdb.com"
    DIR = os.path.join("scripts", "unprocessed", "imsdb")

    if not os.path.exists(DIR):
        os.makedirs(DIR)


    def get_script_from_url(script_url):
        text = ""
        
        try:

            if script_url.endswith('.pdf'):
                text = get_pdf_text(BASE_URL + urllib.parse.quote(script_url))
                return text

            if script_url.endswith('.html'):
                script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
                if len(script_soup.find_all('td', class_="scrtext")) < 1:
                    return ""
                script_text = script_soup.find_all('td', class_="scrtext")[0].pre

                if script_text:
                    script_text = script_soup.find_all('td', class_="scrtext")[0].pre.pre
                    if script_text:
                        text = script_text.get_text()

                    else:
                        script_text = script_soup.find_all('td', class_="scrtext")[0].pre
                        text = script_text.get_text()
        except:
            text = ""

        return text

    def get_script_url(movie):
        script_page_url = movie.contents[0].get('href')
        name = format_filename(movie.contents[0].text)
        movie_name = script_page_url.split("/")[-1].strip('Script.html')

        script_page_soup = get_soup(BASE_URL + urllib.parse.quote(script_page_url))
        paras = script_page_soup.find_all('p', align="center")
        if len(paras) < 1:
            return "", ""
        script_url = paras[0].contents[0].get('href')

        return script_url, name


    soup = get_soup(ALL_URL)
    movielist = soup.find_all('p')

    for movie in tqdm(movielist):
        script_url, name = get_script_url(movie)
        if script_url == "":
            continue
        # if script_url.endswith('.html'):
        #     name = script_url.split("/")[-1].split('.html')[0]
        # elif script_url.endswith('.pdf'):
        #     name = script_url.split("/")[-1].split('.pdf')[0]

        text = get_script_from_url(script_url)

        if text == "" or name == "":
            continue

        name = format_filename(name)

        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)




