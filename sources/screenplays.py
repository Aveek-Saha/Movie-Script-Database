from bs4 import BeautifulSoup
import urllib
import os
import json
from tqdm import tqdm
from .utilities import format_filename, get_soup


def get_screenplays():
    ALL_URL = "https://www.screenplays-online.de/"
    BASE_URL = "https://www.screenplays-online.de/"
    SOURCE = "screenplays"
    DIR = os.path.join("scripts", "unprocessed", SOURCE)
    TEMP_DIR = os.path.join("scripts", "temp", SOURCE)
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    metadata = {}
    soup = get_soup(ALL_URL)
    mlist = soup.find_all(
        'table', class_="screenplay-listing")[0].find_all("a")
    movielist = [x for x in mlist if x.get('href').startswith("screenplay")]

    for movie in tqdm(movielist, desc=SOURCE):
        name = movie.text
        file_name = format_filename(name)
        script_url = BASE_URL + urllib.parse.quote(movie.get('href'))
        # if script_url.startswith("screenplay"):

        script_soup = get_soup(script_url)
        if script_soup == None:
            print("Error fetching ", script_url)
        
        if not script_soup.pre:
            continue
        text = script_soup.pre.get_text()

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
    
    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)