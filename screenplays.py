from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import string

ALL_URL = "https://www.screenplays-online.de/"
BASE_URL = "https://www.screenplays-online.de/"
DIR = os.path.join("scripts", "screenplays")


def format_filename(s):
    valid_chars = "-() %s%s%s" % (string.ascii_letters, string.digits, "%")
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace('%20', ' ')
    filename = filename.replace('%27', '')
    filename = filename.replace(' ', '-')
    return filename


def get_soup(url):
    page = urllib.request.Request(url)
    result = urllib.request.urlopen(page)
    resulttext = result.read()

    soup = BeautifulSoup(resulttext, 'html.parser')
    return soup


soup = get_soup(ALL_URL)
mlist = soup.find_all('table', class_="screenplay-listing")[0].find_all("a")
movielist = [x for x in mlist if x.get('href').startswith("screenplay")]

for movie in tqdm(movielist):
    name = format_filename(movie.text)
    script_url = movie.get('href')
    # if script_url.startswith("screenplay"):

    script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
    # print(script_soup.pre.get_text())
    if not script_soup.pre:
        continue
    text = script_soup.pre.get_text()

    with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
        out.write(text)




