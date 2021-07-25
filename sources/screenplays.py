from bs4 import BeautifulSoup
import urllib
import os
import json
from tqdm import tqdm
from .utilities import format_filename, get_soup, create_script_dirs


def get_screenplays():
    ALL_URL = "https://www.screenplays-online.de/"
    BASE_URL = "https://www.screenplays-online.de/"
    SOURCE = "screenplays"
    DIR, TEMP_DIR, META_DIR = create_script_dirs(SOURCE)

    files = [os.path.join(DIR, f) for f in os.listdir(DIR) if os.path.isfile(
        os.path.join(DIR, f)) and os.path.getsize(os.path.join(DIR, f)) > 3000]

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

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        if os.path.join(DIR, file_name + '.txt') in files:
            continue

        script_soup = get_soup(script_url)
        if script_soup == None:
            print("Error fetching ", script_url)
            metadata.pop(name, None)
            continue
        
        if not script_soup.pre:
            metadata.pop(name, None)
            continue
        text = script_soup.pre.get_text()

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
    
    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)