from os import dup, listdir, makedirs
from os.path import isfile, join, sep, getsize, exists

import urllib
import urllib.request
import re
import json
import string
from unidecode import unidecode
from tqdm.std import tqdm

import config

f = open('sources.json', 'r')
data = json.load(f)

META_DIR = join("scripts", "metadata")
TMDB_URL = "https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1"

tmdb_api_key = config.tmdb_api_key


metadata = {}
for source in data:
    included = data[source]
    meta_file = join(META_DIR, source + ".json")
    if included == "true" and isfile(meta_file):
        with open(meta_file) as json_file:
            source_meta = json.load(json_file)
            metadata[source] = source_meta

forbidden = ["the", "a", "an", "and", "or", "part",
             "vol", "chapter", "movie", "transcript"]
unique = []
origin = {}
for source in metadata:
    DIR = join("scripts", "unprocessed", source)
    files = [join(DIR, f) for f in listdir(DIR) if isfile(
        join(DIR, f)) and getsize(join(DIR, f)) > 3000]
    
    source_meta = metadata[source]
    for script in source_meta:
        name = re.sub(r'\([^)]*\)', '', script.strip()).lower()
        name = " ".join(name.split('-'))
        name = re.sub(r'['+string.punctuation+']', ' ', name)
        name = re.sub(' +', ' ', name).strip()
        name = name.split()
        name = " ".join(list(filter(lambda a: a not in forbidden, name)))
        name = "".join(name.split())
        unique.append(name)
        if name not in origin:
            origin[name] = {"files": []}
        curr_script = metadata[source][script]
        curr_file = join("scripts", "unprocessed", source, curr_script["file_name"] + ".txt") 
        
        if curr_file in files:
            origin[name]["files"].append({
                "name": script,
                "source": source,
                "file_name": curr_script["file_name"],
                "script_url": curr_script["script_url"],
                "size": getsize(curr_file)
            })
            
        else:
            origin.pop(name)

final = sorted(list(set(unique)))
# print(final)
# print(len(final))

# with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
#     json.dump(origin, outfile, indent=4)

print(len(origin))
count = 0
missing_count = 0
for script in tqdm(origin):
    name = origin[script]["files"][0]["name"]
    url = TMDB_URL % (tmdb_api_key, urllib.parse.quote(name))
    response = urllib.request.urlopen(url)
    data = response.read()
    jres = json.loads(data)
    if jres['total_results'] > 0:
        movie = jres['results'][0]
        if "title" in movie and "release_date" in movie and "id" in movie and "overview" in movie:
            origin[script]["tmdb"] = {
                "title": unidecode(movie["title"]),
                "release_date": movie["release_date"],
                "id": movie["id"],
                "overview": unidecode(movie["overview"])
            }
        else:
            missing_count += 1
    else:
        print(name)
        count += 1

with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
    json.dump(origin, outfile, indent=4)

print(count)
print(missing_count)

