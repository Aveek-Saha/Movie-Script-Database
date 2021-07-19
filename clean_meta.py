from os import dup, listdir, makedirs
from os.path import isfile, join, sep, getsize, exists

import urllib
import urllib.request
import re
import json
import string
from unidecode import unidecode
from tqdm.std import tqdm
import multiprocessing

import imdb

import config

ia = imdb.IMDb()

f = open('sources.json', 'r')
data = json.load(f)

META_DIR = join("scripts", "metadata")
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1"
TMDB_TV_URL = "https://api.themoviedb.org/3/search/tv?api_key=%s&language=en-US&query=%s&page=1"

tmdb_api_key = config.tmdb_api_key

forbidden = ["the", "a", "an", "and", "or", "part",
             "vol", "chapter", "movie", "transcript"]

metadata = {}
for source in data:
    included = data[source]
    meta_file = join(META_DIR, source + ".json")
    if included == "true" and isfile(meta_file):
        with open(meta_file) as json_file:
            source_meta = json.load(json_file)
            metadata[source] = source_meta

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

# Remove ", The"
# Remove ", A"
# Split by "_"
# If name has filmed as or released as, use those names instead
# Remove brackets ()
# Remove "Pilot"
# Remove "First Draft"
# Remove "Transcript"
# Remove "Script"
# Remove "Early/Final Pilot TV Script PDF"
# Remove text after ":"

def clean_name(name):
    name = name.lower()
    name = " ".join(name.split("_"))
    
    name = name.replace(", the", "")
    name = name.replace(", a", "")
    
    alt_name = name.split("filmed as")
    if len(alt_name) > 1:
        name = re.sub(r"[\([{})\]]", "", name).split("filmed as")[-1].strip()
    
    alt_name = name.split("released as")
    if len(alt_name) > 1:
        name = re.sub(r"[\([{})\]]", "", name).split("released as")[-1].strip()
        
    name = re.sub(r'\([^)]*\)', '', name)

    name = name.replace("early pilot", "")
    name = name.replace("final pilot", "")
    name = name.replace("transcript", "")
    name = name.replace("first draft", "")
    name = name.replace("tv script pdf", "")
    name = name.replace("pilot", "")
    name = name.strip()

    return name

print(len(origin))
count = 0
missing_count = 0
for script in tqdm(origin):
    # Use original name
    name = origin[script]["files"][0]["name"]
    url = TMDB_MOVIE_URL % (tmdb_api_key, urllib.parse.quote(name))
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
        # Try with cleaned name
        name = clean_name(name)
        url = TMDB_MOVIE_URL % (tmdb_api_key, urllib.parse.quote(name))
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
            # Try with TV search
            url = TMDB_TV_URL % (tmdb_api_key, urllib.parse.quote(name))
            response = urllib.request.urlopen(url)
            data = response.read()
            jres = json.loads(data)
            if jres['total_results'] > 0:
                tv_show = jres['results'][0]
                if "title" in tv_show and "first_air_date" in tv_show and "id" in tv_show and "overview" in tv_show:
                    origin[script]["tmdb"] = {
                        "title": unidecode(tv_show["title"]),
                        "first_air_date": tv_show["first_air_date"],
                        "id": tv_show["id"],
                        "overview": unidecode(tv_show["overview"])
                    }
                else:
                    missing_count += 1
            else:
                print(name)
                count += 1

# with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
#     json.dump(origin, outfile, indent=4)

# print(count)
# print(missing_count)

# f = open(join(META_DIR, "clean_meta.json"), 'r')
# origin = json.load(f)

def get_imdb(name):
    try:
        movies = ia.search_movie(name)
        if len(movies) > 0:
            movie_id = movies[0].movieID
            movie = movies[0]

            if 'year' in movie:
                release_date = movie['year']
            else:
                return {}
            
            return {
                    "title": movie['title'],
                    "release_date": release_date,
                    "id": movie_id,
                }
        else:
            return {}
    except Exception as err:
        print(err)
        return {}

count = 0
for script in tqdm(origin):
    name = origin[script]["files"][0]["name"]
    movie_data = get_imdb(name)

    if not movie_data:
        name = clean_name(name)
        movie_data = get_imdb(name)
        
        if not movie_data:
            print(name)
        else:
            origin[script]["imdb"] = movie_data
    else:
        origin[script]["imdb"] = movie_data

with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
    json.dump(origin, outfile, indent=4)

print(count)
