from bs4 import BeautifulSoup
import urllib
import os
import re

import time
import string

from tqdm import tqdm
from utilities import format_filename, get_soup, get_pdf_text


ALL_URL = "https://www.scriptslug.com/request/?pg="
BASE_URL = "https://www.scriptslug.com/assets/uploads/scripts/"
DIR = os.path.join("scripts", "unprocessed", "scriptslug")

# if not os.path.exists(DIR):
#     os.makedirs(DIR)


def get_script_from_url(script_url):
    text = ""
    
    # try:
    print(script_url)
    text = get_pdf_text(BASE_URL + urllib.parse.quote(script_url) + ".pdf")
    return text

    # except:
    #     text = ""

    return text

# def get_script_url(movie):
#     script_page_url = movie.contents[0].get('href')
#     name = format_filename(movie.contents[0].text)
#     movie_name = script_page_url.split("/")[-1].strip('Script.html')

#     script_page_soup = get_soup(BASE_URL + urllib.parse.quote(script_page_url))
#     paras = script_page_soup.find_all('p', align="center")
#     if len(paras) < 1:
#         return "", ""
#     script_url = paras[0].contents[0].get('href')

#     return script_url, name

for num in range(2):
    pg = num + 1
    soup = get_soup(ALL_URL + str(pg))
    linklist = soup.find_all(class_="script__wrap")
    for link in linklist[:2]:

        script_url = link['href'].split("/")[-1]

        text = get_script_from_url(script_url)
        if text == "" or name == "":
            continue

        name = link.find_all(class_="script__title")[0].find(text=True, recursive=False)
        file_name = re.sub(r'\([^)]*\)', '', format_filename(name.strip()))

        print(text)




# for movie in tqdm(movielist):
#     script_url, name = get_script_url(movie)
#     if script_url == "":
#         continue
#     # if script_url.endswith('.html'):
#     #     name = script_url.split("/")[-1].split('.html')[0]
#     # elif script_url.endswith('.pdf'):
#     #     name = script_url.split("/")[-1].split('.pdf')[0]

#     text = get_script_from_url(script_url)

#     if text == "" or name == "":
#         continue

#     name = format_filename(name)

#     with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
#         out.write(text)




