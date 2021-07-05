from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import string
import re
from .utilities import format_filename, get_soup


def get_actorpoint():
    ALL_URL = "https://www.actorpoint.com/movie-scripts/mscr-%s.html"
    BASE_URL = "https://www.actorpoint.com"
    DIR = os.path.join("scripts", "unprocessed", "actorpoint")

    if not os.path.exists(DIR):
        os.makedirs(DIR)

    def get_script_from_url(script_url):
        text = ""

        try:
            if script_url.endswith('.html'):
                script_soup = get_soup(
                    BASE_URL + urllib.parse.quote(script_url))
                text = script_soup.pre.get_text()
            else:
                print("No script at " + script_url)

        except Exception as err:
            print(err)
            text = ""

        return text

    def get_script_url(movie):

        script_url = movie.a['href']

        name = movie.a.text
        file_name = re.sub(r'\([^)]*\)', '', format_filename(name.strip()))

        return script_url, file_name

    alphabet = string.ascii_lowercase

    movielist = []
    for letter in alphabet:
        soup = get_soup(ALL_URL % (letter))
        movielist.extend(soup.find_all(attrs={"data-th": "Script name"}))
    soup = get_soup(ALL_URL % "num")
    movielist.extend(soup.find_all(attrs={"data-th": "Script name"}))

    for movie in tqdm(movielist):
        script_url, name = get_script_url(movie)
        text = get_script_from_url(script_url)
        if text == "" or name == "":
            continue

        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
