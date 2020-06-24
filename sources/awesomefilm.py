from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import string
from .utilities import format_filename, get_soup, get_pdf_text, get_doc_text

def get_awesomefilm():
    ALL_URL = "http://www.awesomefilm.com/"
    BASE_URL = "http://www.awesomefilm.com/"
    DIR = os.path.join("scripts", "awesomefilm")

    if not os.path.exists(DIR):
        os.makedirs(DIR)

    soup = get_soup(ALL_URL)
    movielist = list(set(soup.find_all('td', class_="tbl")))

    for movie in tqdm(movielist):
        script_ele = movie.a
        if not script_ele:
            continue
        
        script_url = script_ele.get('href')
        # print()

        text = ""
        name = format_filename(script_ele.text)
        try:
            if script_url.endswith('.pdf'):
                text = get_pdf_text(BASE_URL + urllib.parse.quote(script_url))

            elif script_url.endswith('.doc'):
                text = get_doc_text(BASE_URL + urllib.parse.quote(script_url))
            
            elif script_url.endswith('.txt'):
                f = urllib.request.urlopen(BASE_URL + script_url)
                text = f.read().decode("utf-8", errors="ignore")

            else:
                script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
                page = script_soup.pre
                if page:
                    text = page.get_text()
        except:
            print(script_url)
            continue

        if text == "":
            continue

        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)
            

# print(len(movielist))
