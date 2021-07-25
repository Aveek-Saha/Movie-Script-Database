from bs4 import BeautifulSoup
import urllib
import os
import json
from tqdm import tqdm
import string
import re
from .utilities import format_filename, get_soup, create_script_dirs


def get_actorpoint():
    ALL_URL = "https://www.actorpoint.com/movie-scripts/mscr-%s.html"
    BASE_URL = "https://www.actorpoint.com"
    SOURCE = "actorpoint"
    DIR, TEMP_DIR, META_DIR = create_script_dirs(SOURCE)

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
            print(script_url)
            print(err)
            text = ""

        return text

    def get_script_url(movie):

        script_url = movie.a['href']

        name = re.sub(r'\([^)]*\)', '', movie.a.text).strip()
        file_name = format_filename(name)

        return script_url, file_name, name

    files = [os.path.join(DIR, f) for f in os.listdir(DIR) if os.path.isfile(
        os.path.join(DIR, f)) and os.path.getsize(os.path.join(DIR, f)) > 3000]
    alphabet = string.ascii_lowercase
    metadata = {}
    movielist = []

    for letter in alphabet:
        soup = get_soup(ALL_URL % (letter))
        movielist.extend(soup.find_all(attrs={"data-th": "Script name"}))
    soup = get_soup(ALL_URL % "num")
    movielist.extend(soup.find_all(attrs={"data-th": "Script name"}))

    for movie in tqdm(movielist, desc=SOURCE):
        script_url, file_name, name = get_script_url(movie)
        script_url = BASE_URL + urllib.parse.quote(script_url)

        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        if os.path.join(DIR, file_name + '.txt') in files:
            continue

        text = get_script_from_url(script_url)
        if text == "" or name == "":
            metadata.pop(name, None)
            continue

        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)

    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile:
        json.dump(metadata, outfile, indent=4)
