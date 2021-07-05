from bs4 import BeautifulSoup
import urllib
import os

from tqdm import tqdm
from utilities import format_filename, get_soup, get_pdf_text


# def get_imsdb():
ALL_URL = "https://scriptpdf.com/full-list/"
BASE_URL = "https://scriptpdf.com/"
DIR = os.path.join("scripts", "unprocessed", "scriptpdf")

# if not os.path.exists(DIR):
#     os.makedirs(DIR)
def get_script_from_url(script_url):
    text = ""
    try:
        if script_url.endswith('.pdf'):
            text = get_pdf_text(urllib.parse.quote(script_url))
            return text

    except Exception as err:
        print(err)
        text = ""

    return text

def get_script_url(movie):
    script_url = movie.href
    name = format_filename(movie.text)
    
    return script_url, name

soup = get_soup(ALL_URL)
movielist = soup.find_all('a')
for movie in movielist:
    if movie['href'].endswith('.pdf'):
        script_url, name = get_script_url(movie)
        text = get_script_from_url(script_url)

        if text == "" or name == "":
            continue

        with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)