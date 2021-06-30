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

for source in data:
    included = data[source]
    if included == "true":
        DIR = join("scripts", "unprocessed", source)
        data[source] = {}
        data[source]['files'] = [join(DIR, f) for f in listdir(DIR) if isfile(
            join(DIR, f)) and getsize(join(DIR, f)) > 3000]
        data[source]['counts'] = 0

DIR_FILTER = join("scripts", "filtered")
DIR_FINAL = join("scripts", "final")

forbidden = ["the", "a", "an", "and", "or", "part",
             "vol", "chapter", "movie"]
symbols = ["!", "@", "#", "$", "%", "^", "&", "*",
           "_", "-", "+", ":", ".", ",", "?", "\'", "/"]


def remove_duplicates(arr, comb):

    for (x, y) in tqdm(comb):
        x = x.split('.txt')[0]
        y = y.split('.txt')[0]

        name_x = x.split(sep)[-1].lower().split("-")
        name_y = y.split(sep)[-1].lower().split("-")

        name_x = list(filter(lambda a: a not in forbidden, name_x))
        name_y = list(filter(lambda a: a not in forbidden, name_y))

        name_x = "".join(name_x).strip()
        name_y = "".join(name_y).strip()

        name_x = "".join([x for x in name_x if x not in symbols])
        name_y = "".join([x for x in name_y if x not in symbols])

        if name_x == name_y:
            f1 = open(x + '.txt', 'r', errors="ignore")
            file_1 = f1.read()
            f1.close()
            f2 = open(y + '.txt', 'r', errors="ignore")
            file_2 = f2.read()
            f2.close()

            try:
                if len(file_2.strip()) > len(file_1.strip()):
                    arr.remove(x + '.txt')
                else:
                    arr.remove(y + '.txt')
            except:
                pass

    return arr


for key in data:
    if data[key] != "false":
        arr = data[key]['files']
        print("Remove duplicates from", key, len(arr))
        comb = list(itertools.combinations(arr, 2))
        arr = remove_duplicates(arr, comb)
        print("Non duplicates", len(arr))
        print()

print("Remove duplicates between sources")

all_sources = []
for key in data:
    if data[key] != "false":
        arr = data[key]['files']
        all_sources += arr
        print(len(all_sources))
        comb_all = list(itertools.combinations(all_sources, 2))
        all_sources = remove_duplicates(all_sources, comb_all)
        print(len(all_sources))
        print()


# if not exists(DIR_FILTER):
#     makedirs(DIR_FILTER)


# print("Write cleaned files to new dir")
# for source in tqdm(all_sources):
#     f = open(source, 'r', errors="ignore")
#     data = f.read().strip()
#     out = data.replace(u'\u2018', u"'")
#     out = out.replace(u'\u2019', u"'")
#     out = out.replace(u'\u201c', '')
#     out = out.replace(u'\u201d', '')
#     out = out.replace('"', '')
#     out = out.replace("Script provided for educational purposes. More scripts can be found here: http://www.sellingyourscreenplay.com/library", "")
#     data = out.encode('utf-8', 'ignore').decode('utf-8').strip()
#     f.close()

#     with open(join(DIR_FILTER, source.split(sep)[-1]), 'w', errors="ignore") as out:
#         out.write(data)


print("Remove different versions of scripts with same name")
# filtered = [join(DIR_FILTER, f) for f in listdir(DIR_FILTER)
#             if isfile(join(DIR_FILTER, f)) and getsize(join(DIR_FILTER, f)) > 3000]

filtered = [f for f in all_sources if isfile(f) and getsize(f) > 3000]

print(len(filtered))

comb_filter = list(itertools.combinations(filtered, 2))

for (x, y) in tqdm(comb_filter):
    result = fuzz.ratio("".join(x.split(sep)[-1].split('.txt')[0].split("-")).lower(),
                        "".join(y.split(sep)[-1].split('.txt')[0].split("-")).lower())
    if result > 50:
        f1 = open(x, 'r', errors="ignore")
        file_1 = f1.read().replace("\n", " ").replace(
            "\t", " ").replace(" ", "")
        comp_1 = file_1[:300]
        f1.close()
        f2 = open(y, 'r', errors="ignore")
        file_2 = f2.read().replace("\n", " ").replace(
            "\t", " ").replace(" ", "")
        comp_2 = file_2[:300]
        f2.close()

        result = fuzz.ratio(comp_1, comp_2)
        if result > 80:
            # print("".join(x.split(sep)[-1].split('.txt')[0].split("-")),
            #       "".join(y.split(sep)[-1].split('.txt')[0].split("-")))
            try:
                if len(file_2) > len(file_1):
                    filtered.remove(x)
                else:
                    filtered.remove(y)
            except:
                pass

# print(sorted([x.split(sep)[-1] for x in filtered]))
# print(len(filtered))

if not exists(DIR_FINAL):
    makedirs(DIR_FINAL)

print("Write cleaned files to new dir")
for source in tqdm(filtered):
    f = open(source, 'r', errors="ignore")
    text = f.read().strip()
    text = text.replace(
        "Script provided for educational purposes. More scripts can be found here: http://www.sellingyourscreenplay.com/library", "")
    text = text.strip()
    f.close()

    whitespace = re.compile(r'^[\s]+')
    punctuation = re.compile(r'['+string.punctuation+']')
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

    if final_data.strip() == "":
        continue

    if data[source.split(sep)[-2]] != "false":
        data[source.split(sep)[-2]]['counts'] += 1
    with open(join(DIR_FINAL, source.split(sep)[-1]), 'w', errors="ignore") as out:
        out.write(final_data)

for source in data:
    if data[source] != "false":
        print(source, ":", data[source]['counts'])
