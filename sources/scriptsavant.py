from bs4 import BeautifulSoup
import os
import json
from tqdm import tqdm
from unidecode import unidecode
from .utilities import format_filename, get_soup, get_pdf_text


def get_scriptsavant():
    ALL_URL_1 = "https://thescriptsavant.com/free-movie-screenplays-am/"
    ALL_URL_2 = "https://thescriptsavant.com/free-movie-screenplays-nz/"
    BASE_URL = "http://www.thescriptsavant.com/"
    DIR = os.path.join("scripts", "unprocessed", "scriptsavant")
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)

    metadata = {}
    soup_1 = get_soup(ALL_URL_1)
    soup_2 = get_soup(ALL_URL_2)

    movielist = soup_1.find_all('tbody')[0].find_all('a')
    movielist_2 = soup_2.find_all('div', class_='fusion-text')[0].find_all('a')
    movielist += movielist_2

    for movie in tqdm(movielist):
        name = movie.text.replace("script", "").strip()
        file_name = format_filename(name)
        script_url = movie.get('href')

        if not script_url.endswith('.pdf'):
            continue

        try:
            text = get_pdf_text(script_url)

        except Exception as err:
            print(err)
            continue

        if text == "" or file_name == "":
            continue
        
        metadata[unidecode(name)] = {
            "file_name": file_name,
            "script_url": script_url
        }

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)

    with open(os.path.join(META_DIR, "scriptsavant.json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)