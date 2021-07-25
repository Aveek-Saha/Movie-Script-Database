from bs4 import BeautifulSoup

import urllib
import os
import re
import json

from tqdm import tqdm
from .utilities import format_filename, get_soup, get_pdf_text, create_script_dirs


def get_scriptslug():
    ALL_URL = "https://www.scriptslug.com/request/?pg="
    BASE_URL = "https://www.scriptslug.com/assets/uploads/scripts/"
    SOURCE = "scriptslug"
    DIR, TEMP_DIR, META_DIR = create_script_dirs(SOURCE)

    def get_script_from_url(script_url, file_name):
        text = ""

        try:
            text = get_pdf_text(script_url, os.path.join(SOURCE, file_name))
            return text

        except Exception as err:
            print(script_url)
            print(err)
            text = ""

        return text

    def get_script_url(movie):

        script_url = movie['href'].split("/")[-1]

        name = movie.find_all(class_="script__title")[
            0].find(text=True, recursive=False).strip()
        file_name = re.sub(r'\([^)]*\)', '', format_filename(name))

        return script_url, file_name, name

    files = [os.path.join(DIR, f) for f in os.listdir(DIR) if os.path.isfile(
        os.path.join(DIR, f)) and os.path.getsize(os.path.join(DIR, f)) > 3000]

    metadata = {}
    movielist = []

    for num in range(25):
        pg = num + 1
        soup = get_soup(ALL_URL + str(pg))
        linklist = soup.find_all(class_="script__wrap")
        movielist.extend(linklist)

    for movie in tqdm(movielist, desc=SOURCE):
        script_url, file_name, name = get_script_url(movie)
        script_url = BASE_URL + urllib.parse.quote(script_url) + ".pdf"

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        if os.path.join(DIR, file_name + '.txt') in files:
            continue

        text = get_script_from_url(script_url, file_name)
        if text == "" or name == "":
            metadata.pop(name, None)
            continue

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
    
    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)
