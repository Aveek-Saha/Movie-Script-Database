from bs4 import BeautifulSoup

import urllib
import os
import re
import json

from tqdm import tqdm
from .utilities import format_filename, get_soup, get_pdf_text


def get_scriptslug():
    ALL_URL = "https://www.scriptslug.com/request/?pg="
    BASE_URL = "https://www.scriptslug.com/assets/uploads/scripts/"
    DIR = os.path.join("scripts", "unprocessed", "scriptslug")
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)

    def get_script_from_url(script_url):
        text = ""

        try:
            text = get_pdf_text(script_url)
            return text

        except Exception as err:
            print(err)
            text = ""

        return text

    def get_script_url(movie):

        script_url = movie['href'].split("/")[-1]

        name = movie.find_all(class_="script__title")[
            0].find(text=True, recursive=False).strip()
        file_name = re.sub(r'\([^)]*\)', '', format_filename(name))

        return script_url, file_name, name

    metadata = {}
    movielist = []

    for num in range(25):
        pg = num + 1
        soup = get_soup(ALL_URL + str(pg))
        linklist = soup.find_all(class_="script__wrap")
        movielist.extend(linklist)

    for movie in tqdm(movielist):
        script_url, file_name, name = get_script_url(movie)
        script_url = BASE_URL + urllib.parse.quote(script_url) + ".pdf"
        text = get_script_from_url(script_url)
        if text == "" or name == "":
            continue

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
    
    with open(os.path.join(META_DIR, "scriptslug.json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)
