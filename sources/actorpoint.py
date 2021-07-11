from bs4 import BeautifulSoup
import urllib
import os
import json
from tqdm import tqdm
import string
import re
from .utilities import format_filename, get_soup


def get_actorpoint():
    ALL_URL = "https://www.actorpoint.com/movie-scripts/mscr-%s.html"
    BASE_URL = "https://www.actorpoint.com"
    DIR = os.path.join("scripts", "unprocessed", "actorpoint")
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)

    def get_script_from_url(script_url):
        text = ""

        try:
            if script_url.endswith('.html'):
                script_soup = get_soup(script_url)
                if script_soup == None:
                    return ""
                text = script_soup.pre.get_text()
            else:
                print("No script at " + script_url)

        except Exception as err:
            print(err)
            text = ""

        return text

    def get_script_url(movie):

        script_url = movie.a['href']

        name = re.sub(r'\([^)]*\)', '', movie.a.text.strip())
        file_name = format_filename(name)

        return script_url, file_name, name

    alphabet = string.ascii_lowercase
    metadata = {}
    movielist = []

    for letter in alphabet:
        soup = get_soup(ALL_URL % (letter))
        movielist.extend(soup.find_all(attrs={"data-th": "Script name"}))
    soup = get_soup(ALL_URL % "num")
    movielist.extend(soup.find_all(attrs={"data-th": "Script name"}))

    for movie in tqdm(movielist):
        script_url, file_name, name = get_script_url(movie)
        script_url = BASE_URL + urllib.parse.quote(script_url)

        text = get_script_from_url(script_url)
        if text == "" or name == "":
            continue

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
    
    with open(os.path.join(META_DIR, "actorpoint.json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)
