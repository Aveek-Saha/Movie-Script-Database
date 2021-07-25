from bs4 import BeautifulSoup
import os
import json
from tqdm import tqdm
import re
from .utilities import format_filename, get_soup, get_pdf_text, create_script_dirs


def get_sfy():
    ALL_URL = "https://sfy.ru/scripts"
    BASE_URL = "https://sfy.ru"
    SOURCE = "sfy"
    DIR, TEMP_DIR, META_DIR = create_script_dirs(SOURCE)

    files = [os.path.join(DIR, f) for f in os.listdir(DIR) if os.path.isfile(
        os.path.join(DIR, f)) and os.path.getsize(os.path.join(DIR, f)) > 3000]

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

    for movie in tqdm(movielist, desc=SOURCE):
        script_url = movie.get('href')
        name = clean_name(movie.text)
        file_name = format_filename(name)

        text = ""
        if not script_url.startswith('https') and not script_url.startswith('http') and not script_url.startswith('www'):
            script_url = BASE_URL + script_url

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        if os.path.join(DIR, file_name + '.txt') in files:
            continue

        if script_url.endswith('.pdf'):
            try:
                text = get_pdf_text(
                    script_url, os.path.join(SOURCE, file_name))
            except Exception as err:
                print(script_url)
                print(err)
                metadata.pop(name, None)
                continue
        else:
            try:
                script_soup = get_soup(script_url).pre
                if script_soup:
                    text = script_soup.get_text()
            except Exception as err:
                print(script_url)
                print(err)
                metadata.pop(name, None)
                continue

        if text == "" or name == "":
            metadata.pop(name, None)
            continue

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)

    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile:
        json.dump(metadata, outfile, indent=4)
