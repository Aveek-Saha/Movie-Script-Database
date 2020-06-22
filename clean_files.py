from fuzzywuzzy import fuzz
from os import listdir, makedirs
from os.path import isfile, join, sep, getsize, exists
from tqdm import tqdm
import re
import itertools

DIR_ISMDB = join("scripts", "ismdb")
DIR_DAILY = join("scripts", "dailyscript")
DIR_WEEKLY = join("scripts", "weeklyscript")
DIR_SCREEN = join("scripts", "screenplays")
DIR_AWESOME = join("scripts", "awesomefilm")

DIR_FILTER = join("scripts", "filtered")
DIR_FINAL = join("scripts", "final")

ismdb = [join(DIR_ISMDB, f) for f in listdir(DIR_ISMDB) if isfile(
    join(DIR_ISMDB, f)) and getsize(join(DIR_ISMDB, f)) > 3000]
daily = [join(DIR_DAILY, f) for f in listdir(DIR_DAILY) if isfile(
    join(DIR_DAILY, f))and getsize(join(DIR_DAILY, f)) > 3000]
weekly = [join(DIR_WEEKLY, f) for f in listdir(DIR_WEEKLY) if isfile(
    join(DIR_WEEKLY, f))and getsize(join(DIR_WEEKLY, f)) > 3000]
screen = [join(DIR_SCREEN, f) for f in listdir(DIR_SCREEN) if isfile(
    join(DIR_SCREEN, f))and getsize(join(DIR_SCREEN, f)) > 3000]
awesome = [join(DIR_AWESOME, f) for f in listdir(DIR_AWESOME) if isfile(
    join(DIR_AWESOME, f))and getsize(join(DIR_AWESOME, f)) > 3000]


def remove_duplicates(arr, comb):

    for (x, y) in tqdm(comb):
        x = x.split('.txt')[0]
        y = y.split('.txt')[0]
        # if x == y:
        #     continue
        result = fuzz.ratio("".join(x.split(sep)[-1].split("-")).lower(),
                            "".join(y.split(sep)[-1].split("-")).lower())
        if result > 98:
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


print("Remove duplicates from ismdb ", len(ismdb))
comb_ismdb = list(itertools.combinations(ismdb, 2))
ismdb = remove_duplicates(ismdb, comb_ismdb)
print("Non duplicates", len(ismdb))
print()

print("Remove duplicates from dailyscript ", len(daily))
comb_daily = list(itertools.combinations(daily, 2))
daily = remove_duplicates(daily, comb_daily)
print("Non duplicates", len(daily))
print()

print("Remove duplicates from weeklyscript ", len(weekly))
comb_weekly = list(itertools.combinations(weekly, 2))
weekly = remove_duplicates(weekly, comb_weekly)
print("Non duplicates", len(weekly))
print()

print("Remove duplicates from screenplays-online ", len(screen))
comb_screen = list(itertools.combinations(screen, 2))
screen = remove_duplicates(screen, comb_screen)
print("Non duplicates", len(screen))
print()

print("Remove duplicates from awesomefilm ", len(awesome))
comb_awesome = list(itertools.combinations(awesome, 2))
awesome = remove_duplicates(awesome, comb_awesome)
print("Non duplicates", len(awesome))
print()

print("Remove duplicates between sources")
all_sources = ismdb + daily
print(len(all_sources))
comb_all = list(itertools.combinations(all_sources, 2))
all_sources = remove_duplicates(all_sources, comb_all)
# print(len(all_sources))
print()

all_sources += weekly
print(len(all_sources))
comb_all = list(itertools.combinations(all_sources, 2))
all_sources = remove_duplicates(all_sources, comb_all)
# print(len(all_sources))
print()

all_sources += screen
print(len(all_sources))
comb_all = list(itertools.combinations(all_sources, 2))
all_sources = remove_duplicates(all_sources, comb_all)
# print(len(all_sources))
print()

all_sources += awesome
print(len(all_sources))
comb_all = list(itertools.combinations(all_sources, 2))
all_sources = remove_duplicates(all_sources, comb_all)
print(len(all_sources))

# print(sorted([x.split(sep)[-1] for x in daily if x not in all_sources]))
# print(sorted([x.split(sep)[-1] for x in all_sources]))

# unfiltered = ismdb + daily + weekly


if not exists(DIR_FILTER):
    makedirs(DIR_FILTER)


print("Write cleaned files to new dir")
for source in tqdm(all_sources):
    f = open(source, 'r', errors="ignore")
    data = f.read().strip()
    f.close()

    with open(join(DIR_FILTER, source.split(sep)[-1]), 'w', errors="ignore") as out:
        out.write(data)


print("Remove different versions of scripts with same name")
filtered = [join(DIR_FILTER, f) for f in listdir(DIR_FILTER)
            if isfile(join(DIR_FILTER, f)) and getsize(join(DIR_FILTER, f)) > 3000]
print(len(filtered))
comb_filter = list(itertools.combinations(filtered, 2))

for (x, y) in tqdm(comb_filter):
    f1 = open(x, 'r', errors="ignore")
    file_1 = f1.read(200)
    f1.close()
    f2 = open(y, 'r', errors="ignore")
    file_2 = f2.read(200)
    f2.close()

    result = fuzz.ratio(file_1, file_2)
    if result > 95:
        try:
            if len(file_2) > len(file_1):
                filtered.remove(x)
            else:
                filtered.remove(y)
        except:
            pass

print(sorted([x.split(sep)[-1] for x in filtered]))
print(len(filtered))

if not exists(DIR_FINAL):
    makedirs(DIR_FINAL)


print("Write cleaned files to new dir")
for source in tqdm(filtered):
    f = open(source, 'r', errors="ignore")
    data = f.read().strip()
    f.close()

    with open(join(DIR_FINAL, source.split(sep)[-1]), 'w', errors="ignore") as out:
        out.write(data)

