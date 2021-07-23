from fuzzywuzzy import fuzz
from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists
from tqdm import tqdm
import re
import itertools
import string

from unidecode import unidecode

import json

f = open('sources.json', 'r')
data = json.load(f)

SCRIPT_DIR = join("scripts", "unprocessed")
META_DIR = join("scripts", "metadata")
CLEAN_DIR = join("scripts", "filtered")
META_FILE = join(META_DIR, "clean_meta.json")
CLEAN_META = join(META_DIR, "clean_files_meta.json")

if not exists(CLEAN_DIR):
    makedirs(CLEAN_DIR)

f = open(META_FILE, 'r')
metadata = json.load(f)


def clean_script(text):

    text = text.encode('utf-8', 'ignore').decode('utf-8').strip()
    text = text.replace("", "")
    text = text.replace("•", "")
    text = text.replace("·", "")

    whitespace = re.compile(r'^[\s]+')
    scenenumber = re.compile(r'^\d+\s+.*\s+\d+$')
    pagenumber = re.compile(
        r'^[(]?\d{1,3}[)]?[\.]?$|^.[(]?\d{1,3}[)]?[\.]?$|^[(]?\d{1,3}[)]?.?[(]?\d{1,3}[)]?[\.]?$')
    cont = re.compile(r'^\(continued\)$|^continued:$|^continued: \(\d+\)$')
    allspecialchars = re.compile(r'^[^\w\s ]*$')

    lines = []

    for line in text.split('\n'):
        copy = line
        line = line.lower().strip()
        # skip lines with one char since they're likely typos
        if len(line) == 1:
            if line.lower() != 'a' or line.lower() != 'i':
                continue
        # skip lines containing page numbers
        if pagenumber.match(line):
            continue
        # Lines which just say continued
        if cont.match(line):
            continue
        # skip lines containing just special characters
        if line != '' and allspecialchars.match(line):
            continue
        # Filter lines with numbers before and after scene details
        if scenenumber.match(line):
            numbers = copy.split()
            if numbers[0] == numbers[-1]:
                copy = " ".join(numbers[1:-1]).strip()
                line = copy.lower().strip()
        # Lines which just say continued
        if cont.match(line):
            continue
        if line == "omitted":
            continue
        lines.append(copy.strip())

    final_data = '\n'.join(lines)
    final_data = re.sub(r'\n\n+', '\n\n', final_data).strip()
    return final_data


def compare_scripts(scripts):
    combos = list(itertools.combinations(scripts, 2))

    for combo in combos:
        if combo[0]["text"] == combo[1]["text"]:
            index_1 = next((index for (index, d) in enumerate(
                scripts) if d["source"] == combo[0]["source"]), None)
            index_2 = next((index for (index, d) in enumerate(
                scripts) if d["source"] == combo[1]["source"]), None)
            scripts[index_1]["matches"] += 1
            scripts[index_2]["matches"] += 1

    return sorted(scripts, key=lambda i: (i['matches'], i["size"]), reverse=True)[0]


def get_clean_text(path):
    f = open(path, 'r', errors="ignore")
    text = f.read()
    f.close()
    clean_text = clean_script(text).strip()

    return clean_text


clean_dict = {}

count = 0
count_total = 0
for script in tqdm(metadata):
    files = metadata[script]["files"]
    if len(files) == 1:
        path = join(SCRIPT_DIR, files[0]["source"],
                    files[0]["file_name"] + ".txt")
        clean_text = get_clean_text(path)

        if clean_text.strip() == "":
            print(files)
            continue

        clean_dict[script] = {"file": files[0]}
        if "tmdb" in metadata[script]:
            clean_dict[script]["tmdb"] = metadata[script]["tmdb"]
        if "imdb" in metadata[script]:
            clean_dict[script]["imdb"] = metadata[script]["imdb"]

    else:
        script_arr = []

        for file in files:
            path = join(SCRIPT_DIR, file["source"],
                        file["file_name"] + ".txt")
            clean_text = get_clean_text(path)
            if clean_text.strip() == "":
                print(files)
                continue
            file["text"] = clean_text[:10000]
            file["matches"] = 0

            script_arr.append(file)
        final = compare_scripts(script_arr)
        final.pop('text', 'No Key found')
        final.pop('matches', 'No Key found')

        clean_dict[script] = {"file": final}
        if "tmdb" in metadata[script]:
            clean_dict[script]["tmdb"] = metadata[script]["tmdb"]
        if "imdb" in metadata[script]:
            clean_dict[script]["imdb"] = metadata[script]["imdb"]

    clean_dict[script]["file"].pop('size', 'No Key found')

    path = join(SCRIPT_DIR, clean_dict[script]["file"]["source"],
                clean_dict[script]["file"]["file_name"] + ".txt")
    clean_text = get_clean_text(path)

    with open(join(CLEAN_DIR, clean_dict[script]["file"]["file_name"] + ".txt"), 'w', errors="ignore") as out:
        out.write(clean_text)

with open(join(CLEAN_META), "w") as outfile:
    json.dump(clean_dict, outfile, indent=4)

print("Total scripts: ", len(clean_dict))
# print(count_total)

count = 0
score = {}
for script in clean_dict:
    if "tmdb" in clean_dict[script] and "imdb" in clean_dict[script]:
        count += 1
    if clean_dict[script]["file"]["source"] in score:
        score[clean_dict[script]["file"]["source"]] +=1
    else:
        score[clean_dict[script]["file"]["source"]] =1

print("Scripts with complete metadata: ", count)
print("Source Breakdown: ", score)