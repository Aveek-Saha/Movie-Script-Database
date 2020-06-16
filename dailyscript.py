from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm

ALL_URL_1 = "https://www.dailyscript.com/movie.html"
ALL_URL_2 = "https://www.dailyscript.com/movie_n-z.html"
BASE_URL = "https://www.dailyscript.com/"
DIR = os.path.join("scripts", "dailyscript")


def get_soup(url):
    page = urllib.request.Request(url)
    result = urllib.request.urlopen(page)
    resulttext = result.read()

    soup = BeautifulSoup(resulttext, 'html.parser')
    return soup


soup_1 = get_soup(ALL_URL_1)
soup_2 = get_soup(ALL_URL_2)

movielist = soup_1.find_all('ul')[0].find_all('p')
movielist_2 = soup_2.find_all('ul')[0].find_all('p')
movielist += movielist_2

# print(movielist)

for movie in tqdm(movielist):
    script_url = movie.contents
    if len(script_url) < 2:
        continue
    script_url = movie.find('a').get('href')
    print(script_url)

    text = ""

    if script_url.endswith('.pdf'):
        continue

    elif script_url.endswith('.html') or script_url.endswith('.htm'):
        script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
        text = script_soup.pre.get_text()
    
    elif script_url.endswith('.txt'):
        script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
        text = script_soup.get_text()

    if text == "":
        continue

    with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
        out.write(text)
