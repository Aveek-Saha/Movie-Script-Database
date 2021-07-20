import urllib
import urllib.request
import json
from tqdm import tqdm
from os.path import isfile, join, sep, getsize, exists
from os import listdir, makedirs
import re
from fuzzywuzzy import fuzz
import unidecode

import config

DIR_FINAL = join("scripts", "final")


tmdb_api_key = config.tmdb_api_key
omdb_api_key = config.omdb_api_key

movielist = [join(DIR_FINAL, f) for f in listdir(DIR_FINAL) if isfile(
    join(DIR_FINAL, f)) and getsize(join(DIR_FINAL, f)) > 3000]

if not exists("metadata"):
    makedirs("metadata")


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


def average_ratio(n, m):
    return ((fuzz.token_sort_ratio(n,  m) + fuzz.token_sort_ratio(m,  n)) // 2)


def roman_to_int(num):
    string = num.split()
    res = []
    for s in string:
        if s == "ii":
            res.append("2")
        elif s == "iii":
            res.append("3")
        elif s == "iv":
            res.append("4")
        elif s == "v":
            res.append("5")
        elif s == "vi":
            res.append("6")
        elif s == "vii":
            res.append("7")
        elif s == "viii":
            res.append("8")
        elif s == "ix":
            res.append("9")
        else:
            res.append(s)
    return " ".join(res)


forbidden = ["the", "a", "an", "and", "or", "part",
             "transcript", "vol", "chapter", "movie"]
symbols = ["!", "@", "#", "$", "%", "^", "&", "*",
           "_", "-", "+", ":", ".", ",", "?", "\'", "/"]


def clean_name(name):
    name = " ".join(name.lower().split("-"))
    name = re.sub(r'\([^)]*\)', '', name)
    name = re.sub(r"(\d{4})", "", name)
    name = "".join([x for x in name if x not in symbols])
    name = name.split()
    name = list(filter(lambda a: a not in forbidden, name))
    name = " ".join(name).strip()
    name = roman_to_int(name)
    name = unidecode.unidecode(name)

    return name


def check_series(name1, name2):
    name1 = "".join(name1.split())
    name2 = "".join(name2.split())

    series_num1 = re.findall(r'\d{1,3}', name1)
    series_num2 = re.findall(r'\d{1,3}', name2)
    series_title1 = re.findall(r'.+?(?=\d)', name1)
    series_title2 = re.findall(r'.+?(?=\d)', name2)
    if len(series_num1) > 0 and len(series_num2) > 0 and len(series_title1) > 0 and len(series_title2) > 0:
        if series_num1[0] == series_num2[0] and series_title1[0] == series_title2[0]:
            return True

    return False


def check_series_number(name1, name2):
    name1 = "".join(name1.split())
    name2 = "".join(name2.split())

    series_num1 = re.findall(r'\d{1,3}', name1)
    series_num2 = re.findall(r'\d{1,3}', name2)

    if len(series_num1) > 0 and len(series_num2) > 0:
        if series_num1[0] == series_num2[0]:
            return True
    elif len(series_num1) == 0 and len(series_num2) == 0:
        return True
    return False


def title_match(title, key):
    if clean_name(title) == clean_name(key) or "".join(clean_name(title).split()) == "".join(clean_name(key).split()) or check_series(clean_name(title), clean_name(key)):
        return True
    elif fuzz.ratio("".join(clean_name(title).split()), "".join(clean_name(key).split())) > 89 and check_series_number(clean_name(title), clean_name(key)):
        return True
    else:
        return False


# Search TMDb for movies
mapping = {}

for movie in tqdm(movielist):
    name = search_name(movie.split(sep)[-1].split('.txt')[0])
    response = urllib.request.urlopen(
        "https://api.themoviedb.org/3/search/movie?api_key=" +
        tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
        + "&page=1")
    html = response.read()
    jres = json.loads(html)
    if jres['total_results'] > 0:
        mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
    else:
        name = movie.split(sep)[-1].split('.txt')[0]
        response = urllib.request.urlopen(
            "https://api.themoviedb.org/3/search/movie?api_key=" +
            tmdb_api_key + "&language=en-US&query=" + urllib.parse.quote(name)
            + "&page=1")
        html = response.read()
        jres = json.loads(html)
        if jres['total_results'] > 0:
            mapping[movie.split(sep)[-1].split('.txt')[0]] = jres['results']
        else:
            name = " ".join(movie.split(sep)[-1].split('.txt')[0].split("-"))
            name = " ".join(camel_case_split(name))
            response = urllib.request.urlopen(
                "https://api.themoviedb.org/3/search/movie?api_key=" +
                tmdb_api_key + "&language=en-US&query=" +
                urllib.parse.quote(name)
                + "&page=1")
            html = response.read()
            jres = json.loads(html)
            if jres['total_results'] > 0:
                mapping[movie.split(sep)[-1].split('.txt')
                        [0]] = jres['results']
            else:
                mapping[movie.split(sep)[-1].split('.txt')[0]] = []

    # print(name)

json_object = json.dumps(mapping, indent=4)

with open(join("metadata", "metadata.json"), "w") as outfile:
    outfile.write(json_object)

with open(join("metadata", "metadata.json"), 'r') as f:
    mapping = json.load(f)


not_found = []

count = 0
movie_info = {}

# Get matching movie from list

for key in mapping:
    if len(mapping[key]) == 0:
        count += 1
        n = key.split('.txt')[0]
        not_found.append(n)
        # print(search_name(key.split('.txt')[0])," : ", n)
        movie_info[key] = {}
    elif len(mapping[key]) > 1:
        for match in mapping[key]:
            if title_match(match['title'], key):
                movie_info[key] = match
                break
        if key not in movie_info:
            n = " ".join(key.replace("transcript", "").split("-"))
            name = re.sub(r'\([^)]*\)', '', n).lower()
            num = re.findall(r'\b\d\b', name)
            date = re.findall(r'\d{4}', n)

            all_titles = [(x['title'], ind)
                          for ind, x in enumerate(mapping[key])]
            all_dates = [(x['release_date'], ind)
                         for ind, x in enumerate(mapping[key]) if 'release_date' in x]

            second = mapping[key][1]

            for title, ind in all_titles:
                n_title = re.findall(r'\b\d\b', title)
                if len(num) > 0 and len(n_title) > 0:
                    if num[0] == n_title[0]:
                        second = mapping[key][ind]
                        break

            for title, ind in all_dates:
                n_title = re.findall(r'\d{4}', title)
                if len(date) > 0 and len(n_title) > 0:
                    if date[0] == n_title[0]:
                        second = mapping[key][ind]
                        break

            m = mapping[key][0]['title'].replace(
                '\'', '').replace(",", '').replace(
                '.', '').replace('&', 'and').lower()
            m2 = second['title'].replace(
                '\'', '').replace(",", '').replace(
                '.', '').replace('&', 'and').lower()
            m = re.sub(r'\([^)]*\)', '', m)
            m2 = re.sub(r'\([^)]*\)', '', m2)
            if average_ratio(name, m) < average_ratio(name, m2) and abs(average_ratio(name, m) - average_ratio(name, m2)) > 10:
                m = m.split(":", 1)[0]
                m2 = m2.split(":", 1)[0]
                if average_ratio(name, m) < average_ratio(name, m2) and abs(average_ratio(name, m) - average_ratio(name, m2)) > 10:
                    # print(key.split('.txt')[0], " : ", mapping[key]
                    #     [0]['title'], " | ", mapping[key][1]['title'])
                    movie_info[key] = mapping[key][1]
                else:
                    movie_info[key] = mapping[key][0]

            else:
                movie_info[key] = mapping[key][0]

    elif len(mapping[key]) == 1:
        movie_info[key] = mapping[key][0]
    else:
        print("what???")

# print(count)


json_object = json.dumps(movie_info, indent=4)

with open(join("metadata", "info.json"), "w") as outfile:
    outfile.write(json_object)

with open(join("metadata", "info.json"), 'r') as f:
    movie_info = json.load(f)

not_matched = []

count = 0

# Get all movies that dont match

for key in movie_info:
    if movie_info[key]:
        name = re.sub(r'\([^)]*\)', '',
                      " ".join(key.split('.txt')[0].replace("transcript", "").split("-"))).lower().replace("the ", "").replace(" the", "")
        m = movie_info[key]['title'].replace(
            '\'', '').replace(",", '').replace(
            '.', '').replace('&', 'and').lower().replace("the ", "").replace(" the", "")
        m = re.sub(r'\([^)]*\)', '', m)
        m_join = "".join(m.split())
        name = re.sub(r'\([^)]*\)', '', name)
        m_rem = m.replace(":", "")
        m_split = m.split(":", 1)[0]
        m_alt = m.split(":", 1)[1] if len(
            m.split(":", 1)) != 1 else m_split
        if average_ratio(name, m) < 80 and average_ratio(name, m_rem) < 80 and average_ratio(name, m_rem) < 80 and (average_ratio(name, m_split) < 80) and (average_ratio(name, m_alt) < 80) and (average_ratio(name, m_join) < 80) and fuzz.partial_ratio(name, m) < 80 and fuzz.partial_ratio(m, name) < 80:
            m_original = movie_info[key]['original_title'].replace(
                '\'', '').replace(",", '').replace(
                '.', '').replace('&', 'and').lower().replace("the ", "").replace(" the", "")
            m_original = re.sub(r'\([^)]*\)', '', m_original)
            if average_ratio(name, m_original) < 80:

                # print(key.split('.txt')[0], " : ", movie_info[key]
                #       ['title'], ' , ', average_ratio(name, m))
                not_matched.append(key)
                count += 1

print(len(not_matched) + len(not_found))


omdb_info = {}

# Search for them in OMDb

for movie in tqdm(not_matched):
    name = search_name(movie.split(sep)[-1].split('.txt')[0])
    response = urllib.request.urlopen(
        "http://www.omdbapi.com/?apikey=" +
        omdb_api_key + "&t=" + urllib.parse.quote(name)
        + "&plot=full")
    html = response.read()
    jres = json.loads(html)
    if jres['Response'] != "False":
        omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
    else:
        name = movie.split(sep)[-1].split('.txt')[0]
        response = urllib.request.urlopen(
            "http://www.omdbapi.com/?apikey=" +
            omdb_api_key + "&t=" + urllib.parse.quote(name)
            + "&plot=full")
        html = response.read()
        jres = json.loads(html)
        if jres['Response'] != "False":
            omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
        else:
            name = " ".join(movie.split(sep)[-1].split('.txt')[0].split("-"))
            name = " ".join(camel_case_split(name))
            response = urllib.request.urlopen(
                "http://www.omdbapi.com/?apikey=" +
                omdb_api_key + "&t=" + urllib.parse.quote(name)
                + "&plot=full")
            html = response.read()
            jres = json.loads(html)
            if jres['Response'] != "False":
                omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
            else:
                omdb_info[movie.split(sep)[-1].split('.txt')[0]] = {}

    # print(name)

json_object = json.dumps(omdb_info, indent=4)

with open(join("metadata", "omdb_unmatched.json"), "w") as outfile:
    outfile.write(json_object)

omdb_info = {}

# Search for them in OMDb

for movie in tqdm(not_found):
    name = search_name(movie.split(sep)[-1].split('.txt')[0])
    response = urllib.request.urlopen(
        "http://www.omdbapi.com/?apikey=" +
        omdb_api_key + "&t=" + urllib.parse.quote(name)
        + "&plot=full")
    html = response.read()
    jres = json.loads(html)
    if jres['Response'] != "False":
        omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
    else:
        name = movie.split(sep)[-1].split('.txt')[0]
        response = urllib.request.urlopen(
            "http://www.omdbapi.com/?apikey=" +
            omdb_api_key + "&t=" + urllib.parse.quote(name)
            + "&plot=full")
        html = response.read()
        jres = json.loads(html)
        if jres['Response'] != "False":
            omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
        else:
            name = " ".join(movie.split(sep)[-1].split('.txt')[0].split("-"))
            name = " ".join(camel_case_split(name))
            response = urllib.request.urlopen(
                "http://www.omdbapi.com/?apikey=" +
                omdb_api_key + "&t=" + urllib.parse.quote(name)
                + "&plot=full")
            html = response.read()
            jres = json.loads(html)
            if jres['Response'] != "False":
                omdb_info[movie.split(sep)[-1].split('.txt')[0]] = jres
            else:
                omdb_info[movie.split(sep)[-1].split('.txt')[0]] = {}

    # print(name)

json_object = json.dumps(omdb_info, indent=4)

with open(join("metadata", "omdb_not_found.json"), "w") as outfile:
    outfile.write(json_object)

omdb_all = {}
count = 0
with open(join("metadata", "omdb_not_found.json"), 'r') as f:
    omdb_all = json.load(f)

with open(join("metadata", "omdb_unmatched.json"), 'r') as f:
    omdb_all.update(json.load(f))

tmdb_re = {}

# Find ones not found in OMDb in TMDb by using the first ine in the script

all_missing = not_matched + not_found

for key in tqdm(all_missing):
    # if not omdb_all[key]:
    f = open(join(DIR_FINAL, key + '.txt'), 'r', errors="ignore")
    first_line = f.readline().strip().lower()
    f.close()
    count += 1
    first_line = first_line.replace(
        "\"", "").replace(".", "").replace(":", "")
    if first_line == "fade in":
        continue
    response = urllib.request.urlopen(
        "https://api.themoviedb.org/3/search/movie?api_key=" +
        tmdb_api_key + "&language=en-US&query=" +
        urllib.parse.quote(first_line)
        + "&page=1")
    html = response.read()
    jres = json.loads(html)
    if jres['total_results'] > 0:
        tmdb_re[key] = jres['results']
    else:
        tmdb_re[key] = []

json_object = json.dumps(tmdb_re, indent=4)

with open(join("metadata", "metadata_2.json"), "w") as outfile:
    outfile.write(json_object)
print(count)


omdb_all = {}
movie_info = {}
count = 0
with open(join("metadata", "metadata_2.json"), 'r') as f:
    omdb_all = json.load(f)


for key in omdb_all:
    if len(omdb_all[key]) == 0:
        count += 1
        n = key.split('.txt')[0]
        # print(search_name(key.split('.txt')[0])," : ", n)
        movie_info[key] = {}
    elif len(omdb_all[key]) > 1:
        for match in omdb_all[key]:
            if title_match(match['title'], key):
                movie_info[key] = match
                break
        if key not in omdb_all:
            n = " ".join(key.replace("transcript", "").split("-"))
            name = re.sub(r'\([^)]*\)', '', n).lower()
            num = re.findall(r'\b\d\b', name)
            date = re.findall(r'\d{4}', n)

            all_titles = [(x['title'], ind)
                          for ind, x in enumerate(omdb_all[key])]
            all_dates = [(x['release_date'], ind)
                         for ind, x in enumerate(omdb_all[key]) if 'release_date' in x]

            second = omdb_all[key][1]

            for title, ind in all_titles:
                n_title = re.findall(r'\b\d\b', title)
                if len(num) > 0 and len(n_title) > 0:
                    if num[0] == n_title[0]:
                        second = omdb_all[key][ind]
                        break

            for title, ind in all_dates:
                n_title = re.findall(r'\d{4}', title)
                if len(date) > 0 and len(n_title) > 0:
                    if date[0] == n_title[0]:
                        second = omdb_all[key][ind]
                        break

            m = omdb_all[key][0]['title'].replace(
                '\'', '').replace(",", '').replace(
                '.', '').replace('&', 'and').lower()
            m2 = second['title'].replace(
                '\'', '').replace(",", '').replace(
                '.', '').replace('&', 'and').lower()

            m = re.sub(r'\([^)]*\)', '', m)
            m2 = re.sub(r'\([^)]*\)', '', m2)
            if average_ratio(name, m) < average_ratio(name, m2) and abs(average_ratio(name, m) - average_ratio(name, m2)) > 10:
                m = m.split(":", 1)[0]
                m2 = m2.split(":", 1)[0]
                if average_ratio(name, m) < average_ratio(name, m2) and abs(average_ratio(name, m) - average_ratio(name, m2)) > 10:
                    # print(key.split('.txt')[0], " : ", omdb_all[key]
                    #       [0]['title'], " | ", omdb_all[key][1]['title'])
                    movie_info[key] = omdb_all[key][1]
                else:
                    movie_info[key] = omdb_all[key][0]

            else:
                movie_info[key] = omdb_all[key][0]

    elif len(omdb_all[key]) == 1:
        movie_info[key] = omdb_all[key][0]
    else:
        print("what???")

json_object = json.dumps(movie_info, indent=4)

with open(join("metadata", "info_2.json"), "w") as outfile:
    outfile.write(json_object)


movie_info = {}

with open(join("metadata", "info_2.json"), 'r') as f:
    movie_info = json.load(f)


count = 0
for key in movie_info:
    if movie_info[key]:
        name = re.sub(r'\([^)]*\)', '',
                      " ".join(key.split('.txt')[0].replace("transcript", "").split("-"))).lower().replace("the ", "").replace(" the", "")
        m = movie_info[key]['title'].replace(
            '\'', '').replace(",", '').replace(
            '.', '').replace('&', 'and').lower().replace("the ", "").replace(" the", "")
        m = re.sub(r'\([^)]*\)', '', m)
        m_join = "".join(m.split())
        name = re.sub(r'\([^)]*\)', '', name)
        m_rem = m.replace(":", "")
        m_split = m.split(":", 1)[0]
        m_alt = m.split(":", 1)[1] if len(
            m.split(":", 1)) != 1 else m_split
        if average_ratio(name, m) < 80 and average_ratio(name, m_rem) < 80 and average_ratio(name, m_rem) < 80 and (average_ratio(name, m_split) < 80) and (average_ratio(name, m_alt) < 80) and (average_ratio(name, m_join) < 80) and fuzz.partial_ratio(name, m) < 80 and fuzz.partial_ratio(m, name) < 80:
            m_original = movie_info[key]['original_title'].replace(
                '\'', '').replace(",", '').replace(
                '.', '').replace('&', 'and').lower().replace("the ", "").replace(" the", "")
            m_original = re.sub(r'\([^)]*\)', '', m_original)
            if average_ratio(name, m_original) < 55:

                print(key.split('.txt')[0], " : ", movie_info[key]
                      ['title'], ' , ', average_ratio(name, m_original))
                count += 1


# print(count)


meta = {}
count = 0
with open(join("metadata", "info.json"), 'r') as f:
    meta = json.load(f)

with open(join("metadata", "info_2.json"), 'r') as f:
    meta.update(json.load(f))

titles = {}

for key in meta:
    if meta[key]:
        if not meta[key]['title'] in titles:
            titles[meta[key]['title']] = []
        titles[meta[key]['title']].append(key)

forbidden = ["the", "a", "an", "and", "or",
             "part", "vol", "chapter", "movie"]

for key in titles:
    if len(titles[key]) > 1:
        # print(key, titles[key])
        for title in titles[key]:
            if clean_name(title) == clean_name(key) or "".join(clean_name(title).split()) == "".join(clean_name(key).split()):
                # count += 1
                # print(key, title)
                for t in titles[key]:
                    if t != title:
                        meta[t] = {}
                break

json_object = json.dumps(meta, indent=4)

with open(join("metadata", "tmdb.json"), "w") as outfile:
    outfile.write(json_object)

meta_2 = {}
with open(join("metadata", "omdb_not_found.json"), 'r') as f:
    meta_2 = json.load(f)

with open(join("metadata", "omdb_unmatched.json"), 'r') as f:
    meta_2.update(json.load(f))

json_object = json.dumps(meta_2, indent=4)

with open(join("metadata", "omdb.json"), "w") as outfile:
    outfile.write(json_object)

for key in meta_2:
    if meta_2[key]:
        if not meta[key]:
            meta[key] = meta_2[key]
    # if not meta[key]:
    #     print(key)

# for key in meta:
#     if meta[key]:
#         title = meta[key]['title']
#         title_match(title, key)


# with open(join("metadata", "metadata.json"), 'r') as f:
#     mapping = json.load(f)

# with open(join("metadata", "metadata_2.json"), 'r') as f:
#     mapping.update(json.load(f))

# movie_info = {}

# for key in mapping:
#     if len(mapping[key]) == 0:
#         movie_info[key] = {}
#     elif len(mapping[key]) > 1:
#         for match in mapping[key]:
#             if title_match(match['title'], key):
#                 movie_info[key] = match
#                 break
#         if key not in movie_info:
#             movie_info[key] = {}
#     elif len(mapping[key]) == 1:
#         movie_info[key] = mapping[key][0]
#     else:
#         print("what???")

# print(count)

# for key in meta:
#     if meta[key]:
#         count += 1
#     else:
#         print(key)

# print(count)
