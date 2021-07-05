from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import re
from .utilities import format_filename, get_soup, get_pdf_text


def get_weeklyscript():
    ALL_URL = "https://www.weeklyscript.com/movies_full_list.htm"
    BASE_URL = "https://www.weeklyscript.com/"
    DIR = os.path.join("scripts", "unprocessed", "weeklyscript")

    if not os.path.exists(DIR):
        os.makedirs(DIR)

    soup = get_soup(ALL_URL)
    movielist = soup.find_all('center')[0].find_all('a')[2:]

    # print(len(movielist))
    for movie in tqdm(movielist):
        script_url = movie.get("href")
        text = ""
        name = ""

        if script_url.endswith('.pdf'):
            text = get_pdf_text(BASE_URL + urllib.parse.quote(script_url))
            name = script_url.split("/")[-1].split('.pdf')[0]

        else:
            script_soup = get_soup(BASE_URL + urllib.parse.quote(
                script_url.replace('.txt', '.html'), safe="%/:=&?~#+!$,;'@()*[]"))
            center = script_soup.find_all("center")[0]
            unwanted = center.find_all(
                'div') + center.find_all('script') + center.find_all('ins')
            for tag in unwanted:
                tag.extract()
            text = center.get_text().strip()
            if script_url.endswith('.html'):
                name = script_url.split("/")[-1].split('.html')[0]
            elif script_url.endswith('.htm'):
                name = script_url.split("/")[-1].split('.htm')[0]
            elif script_url.endswith('.txt'):
                name = script_url.split("/")[-1].split('.txt')[0]

        if text == "" or name == "":
            continue

        name = re.sub(r'\([^)]*\)', '', format_filename(name)).strip()

        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
