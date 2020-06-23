from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import string
import re
from utilities import format_filename, get_soup, get_pdf_text

ALL_URL = "https://sfy.ru/scripts"
BASE_URL = "https://sfy.ru"
DIR = os.path.join("scripts", "sfy")

if not os.path.exists(DIR):
    os.makedirs(DIR)

soup = get_soup(ALL_URL)
movielist = soup.find_all('div', class_='row')[1]
unwanted = movielist.find('ul')
unwanted.extract()
movielist = movielist.find_all('a')

print(len(movielist))

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
        except:
            continue
    else:
        try:
            script_soup = get_soup(script_url).pre
            if script_soup:
                text = script_soup.get_text()
        except:
            continue

    if text == "" or name == "":
        continue

    with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
        out.write(text)
