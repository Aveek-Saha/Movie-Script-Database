from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import string
from .utilities import format_filename, get_soup, get_pdf_text, get_doc_text

def get_scriptsavant():
    ALL_URL_1 = "https://thescriptsavant.com/free-movie-screenplays-am/"
    ALL_URL_2 = "https://thescriptsavant.com/free-movie-screenplays-nz/"
    BASE_URL = "http://www.awesomefilm.com/"
    DIR = os.path.join("scripts", "scriptsavant")

    if not os.path.exists(DIR):
        os.makedirs(DIR)

    soup_1 = get_soup(ALL_URL_1)
    soup_2 = get_soup(ALL_URL_2)

    movielist = soup_1.find_all('tbody')[0].find_all('a')
    movielist_2 = soup_2.find_all('div', class_='fusion-text')[0].find_all('a')
    movielist += movielist_2


    print(len(movielist))
    for movie in tqdm(movielist):
        name = format_filename(movie.text.strip())
        script_url = movie.get('href')

        if not script_url.endswith('.pdf'):
            continue

        try:
            text = get_pdf_text(script_url)

        except:
            continue

        if text == "" or name == "":
            continue
        
        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
