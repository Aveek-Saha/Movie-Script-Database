from bs4 import BeautifulSoup
import urllib
import string

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