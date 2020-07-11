from fuzzywuzzy import fuzz
from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists
from tqdm import tqdm
import re
import itertools
import string

DIR_IMSDB = join("scripts", "unprocessed", "imsdb")
DIR_DAILY = join("scripts", "unprocessed", "dailyscript")
DIR_WEEKLY = join("scripts", "unprocessed", "weeklyscript")
DIR_SCREEN = join("scripts", "unprocessed", "screenplays")
DIR_AWESOME = join("scripts", "unprocessed", "awesomefilm")
DIR_SAVANT = join("scripts", "unprocessed", "scriptsavant")
DIR_SFY = join("scripts", "unprocessed", "sfy")

DIR_FILTER = join("scripts", "filtered")
DIR_FINAL = join("scripts", "final")

imsdb = [join(DIR_IMSDB, f) for f in listdir(DIR_IMSDB) if isfile(
    join(DIR_IMSDB, f)) and getsize(join(DIR_IMSDB, f)) > 3000]
daily = [join(DIR_DAILY, f) for f in listdir(DIR_DAILY) if isfile(
    join(DIR_DAILY, f))and getsize(join(DIR_DAILY, f)) > 3000]
weekly = [join(DIR_WEEKLY, f) for f in listdir(DIR_WEEKLY) if isfile(
    join(DIR_WEEKLY, f))and getsize(join(DIR_WEEKLY, f)) > 3000]
screen = [join(DIR_SCREEN, f) for f in listdir(DIR_SCREEN) if isfile(
    join(DIR_SCREEN, f))and getsize(join(DIR_SCREEN, f)) > 3000]
awesome = [join(DIR_AWESOME, f) for f in listdir(DIR_AWESOME) if isfile(
    join(DIR_AWESOME, f))and getsize(join(DIR_AWESOME, f)) > 3000]
savant = [join(DIR_SAVANT, f) for f in listdir(DIR_SAVANT) if isfile(
    join(DIR_SAVANT, f))and getsize(join(DIR_SAVANT, f)) > 3000]
sfy = [join(DIR_SFY, f) for f in listdir(DIR_SFY) if isfile(
    join(DIR_SFY, f))and getsize(join(DIR_SFY, f)) > 3000]

sources = {
    'savant': savant,
    'imsdb': imsdb,
    'daily': daily,
    'weekly': weekly,
    'screen': screen,
    'awesome': awesome,
    'sfy': sfy
}


def remove_duplicates(arr, comb):

    for (x, y) in tqdm(comb):
        x = x.split('.txt')[0]
        y = y.split('.txt')[0]

        name_x = x.split(sep)[-1].lower().split("-")
        name_y = y.split(sep)[-1].lower().split("-")

        name_x = list(filter(lambda a: a != "the" and a !=
                             "a" and a != "an" and a != "", name_x))
        name_y = list(filter(lambda a: a != "the" and a !=
                             "a" and a != "an" and a != "", name_y))

        name_x = "".join(name_x).strip()
        name_y = "".join(name_y).strip()
        
        # result = fuzz.ratio(name_x , name_y)
        if name_x == name_y:
            f1 = open( x + '.txt', 'r', errors="ignore")
            file_1 = f1.read()
            f1.close()
            f2 = open( y + '.txt', 'r', errors="ignore")
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

for key in sources:
    arr = sources[key]
    print("Remove duplicates from", key, len(arr))
    comb = list(itertools.combinations(arr, 2))
    arr = remove_duplicates(arr, comb)
    print("Non duplicates", len(arr))
    print()

print("Remove duplicates between sources")

all_sources = []
for key in sources:
    arr = sources[key]
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

counts = {
    'scriptsavant': 0,
    'imsdb': 0,
    'dailyscript': 0,
    'weeklyscript': 0,
    'screenplays': 0,
    'awesomefilm': 0,
    'sfy': 0
}

print("Write cleaned files to new dir")
for source in tqdm(filtered):
    f = open(source, 'r', errors="ignore")
    data = f.read().strip()
    data = data.replace(
        "Script provided for educational purposes. More scripts can be found here: http://www.sellingyourscreenplay.com/library", "")
    data = data.encode('utf-8', 'ignore').decode('utf-8').strip()
    f.close()

    whitespace = re.compile(r'^[\s]+')
    punctuation = re.compile(r'['+string.punctuation+']')
    pagenumber = re.compile(
        r'^[(]?\d{1,3}[)]?[\.]?$|^.[(]?\d{1,3}[)]?[\.]?$|^[(]?\d{1,3}[)]?.?[(]?\d{1,3}[)]?[\.]?$')
    cont = re.compile(r'^\(continued\)$|^continued:$')
    allspecialchars = re.compile(r'^[^\w\s ]*$')

    lines = []

    for line in data.split('\n'):
        copy = line
        line = line.lower().strip()

        #skip lines with one char since they're likely typos
        if len(line)==1:
            if line.lower() != 'a' or line.lower() != 'i':
                continue

        #skip lines containing page numbers
        if pagenumber.match(line):
            continue
        
        if cont.match(line):
            continue

        #skip lines containing just special characters
        if line != '' and allspecialchars.match(line):
            continue
            

        lines.append(copy)
    
    final_data = '\n'.join(lines)

    if final_data.strip() == "":
        continue
    counts[source.split(sep)[-2]] += 1
    with open(join(DIR_FINAL, source.split(sep)[-1]), 'w', errors="ignore") as out:
        out.write(final_data)

print(counts)
