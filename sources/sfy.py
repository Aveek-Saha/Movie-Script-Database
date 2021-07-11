from bs4 import BeautifulSoup
import os
import json
from tqdm import tqdm
import re
from .utilities import format_filename, get_soup, get_pdf_text


def get_sfy():
    ALL_URL = "https://sfy.ru/scripts"
    BASE_URL = "https://sfy.ru"
    SOURCE = "sfy"
    DIR = os.path.join("scripts", "unprocessed", SOURCE)
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)

    metadata = {}
    soup = get_soup(ALL_URL)
    movielist = soup.find_all('div', class_='row')[1]
    unwanted = movielist.find('ul')
    unwanted.extract()
    movielist = movielist.find_all('a')

    def clean_name(name):
        name = re.sub(r"(\d{4})", "", name).replace('()', "").strip()
        name = re.sub(' +', ' ', name)

        return name

    for movie in tqdm(movielist):
        script_url = movie.get('href')
        name = clean_name(movie.text)
        file_name = format_filename(name)

        text = ""
        if not script_url.startswith('https'):
            script_url = BASE_URL + script_url

        if script_url.endswith('.pdf'):
            try:
                text = get_pdf_text(script_url)
            except Exception as err:
                print(err)
                continue
        else:
            try:
                script_soup = get_soup(script_url).pre
                if script_soup:
                    text = script_soup.get_text()
            except Exception as err:
                print(err)
                continue

        if text == "" or name == "":
            continue

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
    
    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)
