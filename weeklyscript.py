from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import string

ALL_URL = "https://www.weeklyscript.com/movies_full_list.htm"
BASE_URL = "https://www.weeklyscript.com/"
DIR = os.path.join("scripts", "weeklyscript")

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
movielist = soup.find_all('center')[0].find_all('a')[2:]

# print(len(movielist))
for movie in tqdm(movielist):
    script_url = movie.get("href")
    text = ""
    name = ""

    if script_url.endswith('.pdf'):
        continue

    else:
        # print(BASE_URL + urllib.parse.quote(script_url.replace('.txt',
        #                                                        '.html'), safe="%/:=&?~#+!$,;'@()*[]"))
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

    name = format_filename(name)

    with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
        out.write(text)
