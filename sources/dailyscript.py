from bs4 import BeautifulSoup
import urllib
import os
import json
from tqdm import tqdm
from .utilities import format_filename, get_soup, get_pdf_text


def get_dailyscript():
    ALL_URL_1 = "https://www.dailyscript.com/movie.html"
    ALL_URL_2 = "https://www.dailyscript.com/movie_n-z.html"
    BASE_URL = "https://www.dailyscript.com/"
    SOURCE = "dailyscript"
    DIR = os.path.join("scripts", "unprocessed", SOURCE)
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)

    metadata = {}
    soup_1 = get_soup(ALL_URL_1)
    soup_2 = get_soup(ALL_URL_2)

    movielist = soup_1.find_all('ul')[0].find_all('p')
    movielist_2 = soup_2.find_all('ul')[0].find_all('p')
    movielist += movielist_2

    # print(movielist)

    for movie in tqdm(movielist, desc=SOURCE):
        script_url = movie.contents
        if len(script_url) < 2:
            continue
        script_url = movie.find('a').get('href')
        script_url = BASE_URL + urllib.parse.quote(script_url)

        text = ""
        name = movie.find('a').text.strip()

        if script_url.endswith('.pdf'):
            text = get_pdf_text(script_url, file_name)

        elif script_url.endswith('.html'):
            script_soup = get_soup(script_url)
            if script_soup != None:
                doc = script_soup.pre
                if doc:
                    text = script_soup.pre.get_text()
                else:
                    text = script_soup.get_text()

        elif script_url.endswith('.htm'):
            script_soup = get_soup(script_url)
            if script_soup != None:
                text = script_soup.pre.get_text()

        elif script_url.endswith('.txt'):
            script_soup = get_soup(script_url)
            if script_soup != None:
                text = script_soup.get_text()

        if text == "" or name == "":
            continue

        file_name = format_filename(name)

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
    
    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)
