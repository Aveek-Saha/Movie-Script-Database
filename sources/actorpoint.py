from bs4 import BeautifulSoup
import urllib
import os
from tqdm import tqdm
import string
import re
from utilities import format_filename, get_soup, get_pdf_text, get_doc_text

# def get_actorpoint():
ALL_URL = "https://www.actorpoint.com/movie-scripts/mscr-%s.html"
BASE_URL = "https://www.actorpoint.com"
DIR = os.path.join("scripts", "unprocessed", "actorpoint")

# if not os.path.exists(DIR):
#     os.makedirs(DIR)

def get_script_from_url(script_url):
    text = ""
    
    try:
        if script_url.endswith('.html'):
            script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
            doc = script_soup.pre
            print(doc)
            # text = script_soup.pre.get_text()

    except:
        text = ""

    return text

def get_script_url(movie):
        
    script_url = movie.a['href']

    name = movie.a.text
    file_name = re.sub(r'\([^)]*\)', '', format_filename(name.strip()))

    return script_url, file_name

alphabet = string.ascii_lowercase

movielist = []
for letter in alphabet[:2]:
    soup = get_soup(ALL_URL % (letter))
    movielist.extend(soup.find_all(attrs={"data-th" : "Script name"}))

for movie in tqdm(movielist):
    script_url, name = get_script_url(movie)
    text = get_script_from_url(script_url)
    if text == "" or name == "":
        continue
    

# print(string.ascii_lowercase)

# soup = get_soup(ALL_URL)
# movielist = list(set(soup.find_all('td', class_="tbl")))

# for movie in tqdm(movielist):
#     script_ele = movie.a
#     if not script_ele:
#         continue
    
#     script_url = script_ele.get('href')
#     # print()

#     text = ""
#     name = re.sub(r'\([^)]*\)', '', format_filename(script_ele.text)).strip()
#     try:
#         if script_url.endswith('.pdf'):
#             text = get_pdf_text(BASE_URL + urllib.parse.quote(script_url))

#         elif script_url.endswith('.doc'):
#             text = get_doc_text(BASE_URL + urllib.parse.quote(script_url))
        
#         elif script_url.endswith('.txt'):
#             f = urllib.request.urlopen(BASE_URL + script_url)
#             text = f.read().decode("utf-8", errors="ignore")

#         else:
#             script_soup = get_soup(BASE_URL + urllib.parse.quote(script_url))
#             page = script_soup.pre
#             if page:
#                 text = page.get_text()
#     except:
#         continue

#     if text == "":
#         continue

#     with open(os.path.join(DIR, name + '.txt'), 'w', errors="ignore") as out:
#         out.write(text)
            

