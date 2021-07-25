from bs4 import BeautifulSoup
import os
import json
from tqdm import tqdm
from unidecode import unidecode
from .utilities import format_filename, get_soup, get_pdf_text, create_script_dirs


def get_scriptsavant():
    ALL_URL_1 = "https://thescriptsavant.com/free-movie-screenplays-am/"
    ALL_URL_2 = "https://thescriptsavant.com/free-movie-screenplays-nz/"
    BASE_URL = "http://www.thescriptsavant.com/"
    SOURCE = "scriptsavant"
    DIR, TEMP_DIR, META_DIR = create_script_dirs(SOURCE)

    files = [os.path.join(DIR, f) for f in os.listdir(DIR) if os.path.isfile(
        os.path.join(DIR, f)) and os.path.getsize(os.path.join(DIR, f)) > 3000]

    metadata = {}
    soup_1 = get_soup(ALL_URL_1)
    soup_2 = get_soup(ALL_URL_2)

    movielist = soup_1.find_all('tbody')[0].find_all('a')
    movielist_2 = soup_2.find_all('div', class_='fusion-text')[0].find_all('a')
    movielist += movielist_2

    for movie in tqdm(movielist, desc=SOURCE):
        name = movie.text.replace("script", "").strip()
        file_name = format_filename(name)
        script_url = movie.get('href')

        metadata[unidecode(name)] = {
            "file_name": file_name,
            "script_url": script_url
        }

        if os.path.join(DIR, file_name + '.txt') in files:
            continue

        if not script_url.endswith('.pdf'):
            metadata.pop(name, None)
            continue

        try:
            text = get_pdf_text(script_url, os.path.join(SOURCE, file_name))

        except Exception as err:
            print(script_url)
            print(err)
            continue

        if text == "" or file_name == "":
            metadata.pop(name, None)
            continue
        
        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)

    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)