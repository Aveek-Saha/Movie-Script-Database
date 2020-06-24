import urllib
import urllib.request
import json
from tqdm import tqdm
from os.path import isfile, join, sep, getsize, exists
from os import listdir, makedirs
import re

import config

DIR_FINAL = join("scripts", "final")


tmdb_api_key = config.tmdb_api_key

movielist = [join(DIR_FINAL, f) for f in listdir(DIR_FINAL) if isfile(
    join(DIR_FINAL, f)) and getsize(join(DIR_FINAL, f)) > 3000]

mapping = {}

def camel_case_split(str):
    return re.findall(r'([A-Z0-9]+|[A-Z0-9]?[a-z]+)(?=[A-Z0-9]|\b)', str)

def search_name(name):
    name = " ".join(name.split("-"))
    if re.sub(r"(\d{4})", "", name).strip() != "":
        name = re.sub(r"(\d{4})", "", name)
    name = " ".join(camel_case_split(name)).lower()
    name = re.sub(r'\([^)]*\)', '', name).replace('transcript', "").replace(
        'script', "").replace("early draft", "").replace('transcript', "").replace(
            'production', "").replace("final draft", "").replace(
            'unproduced', "").replace("pdf", "").replace(
            'html', "").replace("doc", "").strip()
    if name.endswith('the') or name.startswith('the '):
        name = name.strip('the').strip()
    if name.endswith('final'):
        name = name.replace('final', "").strip()
    if name.endswith('early'):
        name = name.replace('early', "").strip()
    if name.endswith('shoot'):
        name = name.replace('shoot', "").strip()
    if name.endswith('shooting'):
        name = name.replace('shooting', "").strip()
    name = ' '.join(name.split())
    return name

for movie in tqdm(movielist):
    name = search_name(movie.split(sep)[-1].split('.txt')[0])
    response = urllib.request.urlopen(
        "https://api.themoviedb.org/3/search/movie?api_key=" + 
        tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
        +"&page=1")
    html = response.read()
    jres = json.loads(html)
    if jres['total_results'] > 0:
        mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
    else:
        mapping[movie.split(sep)[-1].split('.txt')[0]] = []

    
    # print(name)

json_object = json.dumps(mapping)

# Writing to sample.json
with open("metadata.json", "w") as outfile:
    outfile.write(json_object)

with open("metadata.json", 'r') as f:
  mapping = json.load(f)

count = 0
for key in mapping:
    if len(mapping[key]) == 0:
        count += 1
        print(search_name(key.split('.txt')[0]))
print(count)
