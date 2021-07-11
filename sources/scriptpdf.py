from bs4 import BeautifulSoup
import urllib
import os
import re
import json
from unidecode import unidecode

from tqdm import tqdm
from .utilities import format_filename, get_soup, get_pdf_text


def get_scriptpdf():
    ALL_URL = "https://scriptpdf.com/full-list/"
    BASE_URL = "https://scriptpdf.com/"
    DIR = os.path.join("scripts", "unprocessed", "scriptpdf")
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)

    def get_script_from_url(script_url):
        text = ""
        try:
            if script_url.endswith('.pdf'):
                text = get_pdf_text(script_url)
                return text

        except Exception as err:
            print(err)
            text = ""

        return text

    def get_script_url(movie):
        script_url = movie['href']
        name = re.sub(r'\([^)]*\)', '', unidecode(movie.text)).strip()
        file_name = format_filename(name)

        return script_url, file_name, name

    metadata = {}
    soup = get_soup(ALL_URL)
    movielist = soup.find_all('a')

    for movie in tqdm(movielist):
        if movie['href'].endswith('.pdf'):
            script_url, file_name, name = get_script_url(movie)

            text = get_script_from_url(script_url)
            if text == "" or name == "":
                continue

            metadata[name] = {
                "file_name": file_name,
                "script_url": script_url
            }

            with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
                out.write(text)
    
    with open(os.path.join(META_DIR, "scriptpdf.json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)
