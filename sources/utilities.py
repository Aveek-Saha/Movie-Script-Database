from bs4 import BeautifulSoup
import urllib.request
import string
import os
import textract
import re


def format_filename(s):
    valid_chars = "-() %s%s%s" % (string.ascii_letters, string.digits, "%")
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace('%20', ' ')
    filename = filename.replace('%27', '')
    filename = filename.replace(' ', '-')
    filename = re.sub(r'-+', '-', filename).strip()
    return filename


def get_soup(url):
    try:
        page = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'})
        result = urllib.request.urlopen(page)
        resulttext = result.read()

        soup = BeautifulSoup(resulttext, 'html.parser')

    except Exception as err:
        print(err)
        soup = None
    return soup


def get_pdf_text(url, name):
    doc = os.path.join("scripts", "temp", name + ".pdf")
    result = urllib.request.urlopen(url)
    f = open(doc, 'wb')
    f.write(result.read())
    f.close()
    try:
        text = textract.process(doc, encoding='utf-8').decode('utf-8')
    except Exception as err:
        print(err)
        text = ""
    # if os.path.isfile(doc):
    #     os.remove(doc)
    return text


def get_doc_text(url, name):
    doc = os.path.join("scripts", "temp", name + ".doc")
    result = urllib.request.urlopen(url)
    f = open(doc, 'wb')
    f.write(result.read())
    f.close()
    try:
        text = textract.process(doc, encoding='utf-8').decode('utf-8')
    except Exception as err:
        print(err)
        text = ""
    # if os.path.isfile(doc):
    #     os.remove(doc)
    return text


def create_script_dirs(source):
    DIR = os.path.join("scripts", "unprocessed", source)
    TEMP_DIR = os.path.join("scripts", "temp", source)
    META_DIR = os.path.join("scripts", "metadata")

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    if not os.path.exists(META_DIR):
        os.makedirs(META_DIR)
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    return DIR, TEMP_DIR, META_DIR
