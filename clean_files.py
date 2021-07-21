from fuzzywuzzy import fuzz
from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists
from tqdm import tqdm
import re
import itertools
import string

import json

f = open('sources.json', 'r')
data = json.load(f)

SCRIPT_DIR = join("scripts", "unprocessed")
META_DIR = join("scripts", "metadata")
CLEAN_DIR = join("scripts", "filtered")
META_FILE = join(META_DIR, "clean_meta_imdb.json")
CLEAN_META = join(META_DIR, "clean_files_meta.json")

if not exists(CLEAN_DIR):
    makedirs(CLEAN_DIR)

f = open(META_FILE, 'r')
metadata = json.load(f)

def clean_script(text):
    
    text = text.encode('utf-8', 'ignore').decode('utf-8').strip()
    text = text.replace("", "")

    whitespace = re.compile(r'^[\s]+')
    pagenumber = re.compile(
        r'^[(]?\d{1,3}[)]?[\.]?$|^.[(]?\d{1,3}[)]?[\.]?$|^[(]?\d{1,3}[)]?.?[(]?\d{1,3}[)]?[\.]?$')
    cont = re.compile(r'^\(continued\)$|^continued:$')
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
        if cont.match(line):
            continue
        # skip lines containing just special characters
        if line != '' and allspecialchars.match(line):
            continue

        lines.append(copy)

    final_data = '\n'.join(lines)
    return final_data

def compare_scripts(scripts):
    combos = list(itertools.combinations(scripts, 2))
    count_same = 0

    for combo in combos:
        if combo[0]["text"] == combo[1]["text"]:
            # print(combo[0]["file_name"], combo[1]["file_name"])
            index = next((index for (index, d) in enumerate(scripts) if d["source"] == combo[0]["source"]), None)
            scripts[index]["matches"] += 1
            count_same += 1

    return sorted(scripts, key = lambda i: (i['matches'], i["size"]),reverse=True)[0]

clean_dict = {}

count = 0
count_total = 0
for script in tqdm(metadata):
    files = metadata[script]["files"]
    # if len(files) == 1:
    #     file = join(SCRIPT_DIR, files[0]["source"],
    #                 files[0]["file_name"] + ".txt")
    #     f = open(file, 'r', errors="ignore")
    #     text = f.read()
    #     f.close()
    #     final_data = clean_script(text)

    #     if final_data.strip() == "":
    #         print(files)

    #     with open(join(CLEAN_DIR, files[0]["source"] + "_" + files[0]["file_name"] + ".txt"), 'w', errors="ignore") as out:
    #         out.write(final_data)

    if  len(files) != 1:
        script_arr = []

        for file in files:
            path = join(SCRIPT_DIR, file["source"],
                    file["file_name"] + ".txt")
            f = open(path, 'r', errors="ignore")
            text = f.read()
            f.close()
            clean_text = clean_script(text)
            file["text"] = clean_text[:10000]
            file["matches"] = 0

            script_arr.append(file)
        final = compare_scripts(script_arr)
        final.pop('text', 'No Key found')

        clean_dict[script] = final

   
with open(join(CLEAN_META), "w") as outfile:
    json.dump(clean_dict, outfile, indent=4)

print(len(clean_dict))
# print(count_total)