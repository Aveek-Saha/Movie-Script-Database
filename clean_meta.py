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
TMDB_ID_URL = "https://api.themoviedb.org/3/find/%s?api_key=%s&language=en-US&external_source=imdb_id"
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
        curr_file = join("scripts", "unprocessed", source,
                         curr_script["file_name"] + ".txt")

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


def clean_name(name):
    name = name.lower()
    # Split by "_"
    name = " ".join(name.split("_"))
    # Remove ", The" and ", A"
    name = name.replace(", the", "")
    name = name.replace(", a", "")
    # If name has filmed as or released as, use those names instead
    alt_name = name.split("filmed as")
    if len(alt_name) > 1:
        name = re.sub(r"[\([{})\]]", "", name).split("filmed as")[-1].strip()
    alt_name = name.split("released as")
    if len(alt_name) > 1:
        name = re.sub(r"[\([{})\]]", "", name).split("released as")[-1].strip()
    # Remove brackets ()
    name = re.sub(r'\([^)]*\)', '', name)
    # Remove "Early/Final Pilot TV Script PDF", "Script",
    # "Transcript", "Pilot", "First Draft"
    name = name.replace("early pilot", "")
    name = name.replace("final pilot", "")
    name = name.replace("transcript", "")
    name = name.replace("first draft", "")
    name = name.replace("tv script pdf", "")
    name = name.replace("pilot", "")
    name = name.strip()

    return name


print(len(origin))


def get_tmdb(name, type="movie"):
    if type == "movie":
        base_url = TMDB_MOVIE_URL
        date = "release_date"
        title = "title"
    elif type == "tv":
        base_url = TMDB_TV_URL
        date = "first_air_date"
        title = "name"

    url = base_url % (tmdb_api_key, urllib.parse.quote(name))
    response = urllib.request.urlopen(url)
    res_data = response.read()
    jres = json.loads(res_data)

    if jres['total_results'] > 0:
        movie = jres['results'][0]
        if title in movie and date in movie and "id" in movie and "overview" in movie:
            return {
                "title": unidecode(movie[title]),
                "release_date": movie[date],
                "id": movie["id"],
                "overview": unidecode(movie["overview"])
            }
        else:
            print("Field missing in response")
            return {}
    else:
        return {}


count = 0
missing_count = 0

print("Get metadata from TMDb")

for script in tqdm(origin):
    # Use original name
    name = origin[script]["files"][0]["name"]
    movie_data = get_tmdb(name)

    if movie_data:
        origin[script]["tmdb"] = movie_data

    else:
        # Try with cleaned name
        name = clean_name(name)
        movie_data = get_tmdb(name)

        if movie_data:
            origin[script]["tmdb"] = movie_data

        else:
            # Try with TV search
            tv_data = get_tmdb(name, "tv")

            if tv_data:
                origin[script]["tmdb"] = tv_data

            else:
                print(name)
                count += 1

print(count)
# with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
#     json.dump(origin, outfile, indent=4)

# print(missing_count)

# f = open(join(META_DIR, "clean_meta.json"), 'r')
# origin = json.load(f)

print("Get metadata from IMDb")

def get_imdb(name):
    try:
        movies = ia.search_movie(name)
        if len(movies) > 0:
            movie_id = movies[0].movieID
            movie = movies[0]

            if 'year' in movie:
                release_date = movie['year']
            else:
                print("Field missing in response")
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
            count += 1
        else:
            origin[script]["imdb"] = movie_data
    else:
        origin[script]["imdb"] = movie_data

with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
    json.dump(origin, outfile, indent=4)

print(count)


def get_tmdb_from_id(id):

    url = TMDB_ID_URL % (id, tmdb_api_key)
    response = urllib.request.urlopen(url)
    res_data = response.read()
    jres = json.loads(res_data)

    if len(jres['movie_results']) > 0:
        results = 'movie_results'
        date = "release_date"
        title = "title"
    elif len(jres['tv_results']) > 0:
        results = 'tv_results'
        date = "first_air_date"
        title = "name"
    else:
        return {}
    
    movie = jres[results][0]
    if title in movie and date in movie and "id" in movie and "overview" in movie:
        return {
            "title": unidecode(movie[title]),
            "release_date": movie[date],
            "id": movie["id"],
            "overview": unidecode(movie["overview"])
        }
    else:
        print("Field missing in response")
        return {}

# f = open(join(META_DIR, "clean_meta.json"), 'r')
# origin = json.load(f)

# Use IMDb id to search TMDb
count = 0

for script in tqdm(origin):
    if "imdb" in origin[script] and "tmdb" not in origin[script]:
        # print(origin[script]["files"][0]["name"])
        imdb_id = "tt" + origin[script]["imdb"]["id"]
        movie_data = get_tmdb_from_id(imdb_id)
        if movie_data:
            origin[script]["tmdb"] = movie_data

        else:
            print(origin[script]["imdb"]["title"], imdb_id)
            count += 1
        
with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
    json.dump(origin, outfile, indent=4)

print(count)