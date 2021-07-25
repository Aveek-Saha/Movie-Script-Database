from bs4 import BeautifulSoup
import urllib
import os
import json

from tqdm import tqdm
from .utilities import format_filename, get_soup, get_pdf_text, create_script_dirs


def get_imsdb():
    ALL_URL = "https://imsdb.com/all-scripts.html"
    BASE_URL = "https://imsdb.com"
    SOURCE = "imsdb"
    DIR, TEMP_DIR, META_DIR = create_script_dirs(SOURCE)

    def get_script_from_url(script_url):
        text = ""

        try:

            if script_url.endswith('.pdf'):
                text = get_pdf_text(script_url, os.path.join(SOURCE, file_name))
                return text

            if script_url.endswith('.html'):
                script_soup = get_soup(
                    script_url)
                if script_soup == None:
                    return text
                if len(script_soup.find_all('td', class_="scrtext")) < 1:
                    return ""
                script_text = script_soup.find_all(
                    'td', class_="scrtext")[0].pre

                if script_text:
                    script_text = script_soup.find_all(
                        'td', class_="scrtext")[0].pre.pre
                    if script_text:
                        text = script_text.get_text()

                    else:
                        script_text = script_soup.find_all(
                            'td', class_="scrtext")[0].pre
                        text = script_text.get_text()
        except Exception as err:
            print(script_url)
            print(err)
            text = ""

        return text

    def get_script_url(movie):
        script_page_url = movie.contents[0].get('href')
        name = movie.contents[0].text
        movie_name = script_page_url.split("/")[-1].strip('Script.html')

        script_page_soup = get_soup(
            BASE_URL + urllib.parse.quote(script_page_url))
        if script_page_soup == None:
            return "", name
        paras = script_page_soup.find_all('p', align="center")
        if len(paras) < 1:
            return "", ""
        script_url = paras[0].contents[0].get('href')

        return script_url, name

    files = [os.path.join(DIR, f) for f in os.listdir(DIR) if os.path.isfile(
        os.path.join(DIR, f)) and os.path.getsize(os.path.join(DIR, f)) > 3000]

    metadata = {}
    soup = get_soup(ALL_URL)
    movielist = soup.find_all('p')

    for movie in tqdm(movielist, desc=SOURCE):
        script_url, name = get_script_url(movie)
        if script_url == "":
            continue
        # if script_url.endswith('.html'):
        #     name = script_url.split("/")[-1].split('.html')[0]
        # elif script_url.endswith('.pdf'):
        #     name = script_url.split("/")[-1].split('.pdf')[0]

        script_url = BASE_URL + urllib.parse.quote(script_url)
        file_name = format_filename(name)
        metadata[name] = {
            "file_name": file_name,
            "script_url": script_url
        }

        if os.path.join(DIR, file_name + '.txt') in files:
            continue

        text = get_script_from_url(script_url)

        if text == "" or name == "":
            metadata.pop(name, None)
            continue


        with open(os.path.join(DIR, file_name + '.txt'), 'w', errors="ignore") as out:
            out.write(text)

    with open(os.path.join(META_DIR, SOURCE + ".json"), "w") as outfile: 
        json.dump(metadata, outfile, indent=4)