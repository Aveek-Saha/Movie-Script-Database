from bs4 import BeautifulSoup

import urllib
import os
import re

from tqdm import tqdm
from .utilities import format_filename, get_soup, get_pdf_text


def get_scriptslug():
    ALL_URL = "https://www.scriptslug.com/request/?pg="
    BASE_URL = "https://www.scriptslug.com/assets/uploads/scripts/"
    DIR = os.path.join("scripts", "unprocessed", "scriptslug")

    if not os.path.exists(DIR):
        os.makedirs(DIR)


    def get_script_from_url(script_url):
        text = ""
        
        try:
            text = get_pdf_text(BASE_URL + urllib.parse.quote(script_url) + ".pdf")
            return text

        except Exception as err:
            print(err)
            text = ""

        return text

    def get_script_url(movie):
        
        script_url = movie['href'].split("/")[-1]

        name = movie.find_all(class_="script__title")[0].find(text=True, recursive=False)
        file_name = re.sub(r'\([^)]*\)', '', format_filename(name.strip()))
        

        return script_url, file_name

    movielist = []

    for num in range(25):
        pg = num + 1
        soup = get_soup(ALL_URL + str(pg))
        linklist = soup.find_all(class_="script__wrap")
        movielist.extend(linklist)

    for movie in tqdm(movielist):
        script_url, name = get_script_url(movie)
        text = get_script_from_url(script_url)
        if text == "" or name == "":
            continue

        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
