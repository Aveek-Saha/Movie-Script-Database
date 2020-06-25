import urllib
import urllib.request
import json
from tqdm import tqdm
from os.path import isfile, join, sep, getsize, exists
from os import listdir, makedirs
import re
from fuzzywuzzy import fuzz

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
    name = " ".join(camel_case_split(re.sub(r'\([^)]*\)', '', name))).lower()
    name = name.replace('transcript', "").replace(
        'script', "").replace("early draft", "").replace(
            "first draft", "").replace('transcript', "").replace(
            'production', "").replace("final draft", "").replace(
            'unproduced', "").replace("pdf", "").replace(
            'html', "").replace("doc", "").replace(
            'the ', "").replace(" the", "").strip()
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

# for movie in tqdm(movielist):
#     name = search_name(movie.split(sep)[-1].split('.txt')[0])
#     response = urllib.request.urlopen(
#         "https://api.themoviedb.org/3/search/movie?api_key=" + 
#         tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
#         +"&page=1")
#     html = response.read()
#     jres = json.loads(html)
#     if jres['total_results'] > 0:
#         mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
#     else:
#         name = movie.split(sep)[-1].split('.txt')[0]
#         response = urllib.request.urlopen(
#             "https://api.themoviedb.org/3/search/movie?api_key=" +
#             tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
#             + "&page=1")
#         html = response.read()
#         jres = json.loads(html)
#         if jres['total_results'] > 0:
#             mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
#         else:
#             name = " ".join(movie.split(sep)[-1].split('.txt')[0].split("-"))
#             name = " ".join(camel_case_split(name))
#             response = urllib.request.urlopen(
#                 "https://api.themoviedb.org/3/search/movie?api_key=" +
#                 tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
#                 + "&page=1")
#             html = response.read()
#             jres = json.loads(html)
#             if jres['total_results'] > 0:
#                 mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
#             else:
#                 mapping[movie.split(sep)[-1].split('.txt')[0]] = []

    
#     # print(name)

# json_object = json.dumps(mapping)

# with open(join("metadata", "metadata.json"), "w") as outfile:
#     outfile.write(json_object)

with open(join("metadata", "metadata.json"), 'r') as f:
  mapping = json.load(f)

count = 0
movie_info = {}


for key in mapping:
    if len(mapping[key]) == 0:
        count += 1
        n = key.split('.txt')[0]
        # print(search_name(key.split('.txt')[0])," : ", n)
        movie_info[key] = {}
    elif len(mapping[key]) > 1:
        name = re.sub(r'\([^)]*\)', '',
                    " ".join(key.split('.txt')[0].split("-"))).lower()
        m = mapping[key][0]['title'].replace(
            '\'', '').replace(",", '').replace(
            '.', '').replace('&', 'and').lower()
        m2 = mapping[key][1]['title'].replace(
            '\'', '').replace(",", '').replace(
            '.', '').replace('&', 'and').lower()
        m = re.sub(r'\([^)]*\)', '', m)
        m2 = re.sub(r'\([^)]*\)', '', m2)
        if (fuzz.token_sort_ratio(name,  m) + fuzz.token_sort_ratio(m,  name) // 2) < (fuzz.token_sort_ratio(name,  m2) + fuzz.token_sort_ratio(m2,  name) // 2) and abs((fuzz.token_sort_ratio(name,  m) + fuzz.token_sort_ratio(m,  name) // 2) - (fuzz.token_sort_ratio(name,  m2) + fuzz.token_sort_ratio(m2,  name) // 2)) > 35:
            # print(key.split('.txt')[0], " : ", mapping[key]
            #       [0]['title'], " | ", mapping[key][1]['title'])
            movie_info[key] = mapping[key][1]
        else:
            movie_info[key] = mapping[key][0]
            
    else:
        movie_info[key] = mapping[key][0]

print(count)


json_object = json.dumps(movie_info, indent=4)

with open(join("metadata", "info.json"), "w") as outfile:
    outfile.write(json_object)
