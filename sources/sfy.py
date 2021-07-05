from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import re
from .utilities import format_filename, get_soup, get_pdf_text


def get_sfy():
    ALL_URL = "https://sfy.ru/scripts"
    BASE_URL = "https://sfy.ru"
    DIR = os.path.join("scripts", "unprocessed", "sfy")

    if not os.path.exists(DIR):
        os.makedirs(DIR)

    soup = get_soup(ALL_URL)
    movielist = soup.find_all('div', class_='row')[1]
    unwanted = movielist.find('ul')
    unwanted.extract()
    movielist = movielist.find_all('a')

    for movie in tqdm(movielist):
        script_url = movie.get('href')
        name = re.sub(r"(\d{4})", "", format_filename(
            movie.text)).replace('()', "").strip("-")
        text = ""
        if not script_url.startswith('https'):
            script_url = BASE_URL + script_url

        if script_url.endswith('.pdf'):
            try:
                text = get_pdf_text(script_url)
            except Exception as err:
                print(err)
                continue
        else:
            try:
                script_soup = get_soup(script_url).pre
                if script_soup:
                    text = script_soup.get_text()
            except Exception as err:
                print(err)
                continue

        if text == "" or name == "":
            continue

        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
