from bs4 import BeautifulSoup
import urllib
import os

import time
start = time.time()

from tqdm import tqdm

URL = "https://www.imsdb.com/all%20scripts"
BASE_URL = "https://www.imsdb.com"
# Open the URL
page = urllib.request.Request(URL)
result = urllib.request.urlopen(page)
# Store the HTML page in a variable
resulttext = result.read()

soup = BeautifulSoup(resulttext, 'html.parser')
movielist = soup.find_all('p')

# movie = movielist[3]
for movie in tqdm(movielist):

    script_page_url = movie.contents[0].get('href')
    movie_name = script_page_url.split("/")[-1].strip('Script.html')

    script_page = urllib.request.Request(BASE_URL + urllib.parse.quote(script_page_url))
    result_script_page = urllib.request.urlopen(script_page)
    resulttext_script_page = result_script_page.read()

    script_page_soup = BeautifulSoup(resulttext_script_page, 'html.parser')
    paras = script_page_soup.find_all('p', align="center")
    if len(paras) < 1:
        continue
    script_url = paras[0].contents[0].get('href')

    # print(BASE_URL + urllib.parse.quote(script_url))
    name = script_url.split("/")[-1].strip('.html')
    if not script_url.endswith('.html'):
        continue
    script = urllib.request.Request(BASE_URL + urllib.parse.quote(script_url))
    result_script = urllib.request.urlopen(script)
    resulttext_script = result_script.read()


    script_soup = BeautifulSoup(resulttext_script, 'html.parser')
    if len(script_soup.find_all('td', class_="scrtext")) < 1:
        continue
    script_text = script_soup.find_all('td', class_="scrtext")[0].pre 
    text = ""
    if script_text:
        script_text = script_soup.find_all('td', class_="scrtext")[0].pre.pre
        if script_text:
            text = script_text.get_text()

        else:
            script_text = script_soup.find_all('td', class_="scrtext")[0].pre
            text = script_text.get_text()

        with open(os.path.join("scripts", name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)

    # print(name)

print('It took', time.time()-start, 'seconds')


