from fuzzywuzzy import fuzz
from os import listdir
from os.path import isfile, join, sep
from tqdm import tqdm
import re
import itertools

DIR_ISMDB = join("scripts", "ismdb")
DIR_DAILY = join("scripts", "dailyscript")
DIR_WEEKLY = join("scripts", "weeklyscript")
DIR_SCREEN = join("scripts", "screenplays")

DIR_FILTER = join("scripts", "filtered")

ismdb = [join(DIR_ISMDB, f) for f in listdir(DIR_ISMDB) if isfile(join(DIR_ISMDB, f))]
daily = [join(DIR_DAILY, f) for f in listdir(DIR_DAILY) if isfile(join(DIR_DAILY, f))]
weekly = [join(DIR_WEEKLY, f) for f in listdir(DIR_WEEKLY) if isfile(join(DIR_WEEKLY, f))]
screen = [join(DIR_SCREEN, f) for f in listdir(DIR_SCREEN) if isfile(join(DIR_SCREEN, f))]


def remove_duplicates(arr, comb):

    for (x, y) in tqdm(comb):
        x = x.split('.txt')[0]
        y = y.split('.txt')[0]
        if x == y:
            continue
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
                print(x + '.txt', y + '.txt')
                return []

    return arr


print("Remove duplicates from ismdb ", len(ismdb))
comb_ismdb = list(itertools.combinations(ismdb, 2))
ismdb = remove_duplicates(ismdb, comb_ismdb)
print()

print("Remove duplicates from dailyscript ", len(daily))
comb_daily = list(itertools.combinations(daily, 2))
daily = remove_duplicates(daily, comb_daily)
print()

print("Remove duplicates from weeklyscript ", len(weekly))
comb_weekly = list(itertools.combinations(weekly, 2))
weekly = remove_duplicates(weekly, comb_weekly)
print()

print("Remove duplicates from screenplays-online ", len(screen))
comb_screen = list(itertools.combinations(screen, 2))
screen = remove_duplicates(screen, comb_screen)
print()

print("Remove duplicates between sources")
all_sources = ismdb + daily
print(len(all_sources))
comb_all = list(itertools.combinations(all_sources, 2))
all_sources = remove_duplicates(all_sources, comb_all)
print(len(all_sources))
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
print(len(all_sources))

unfiltered = ismdb + daily + weekly

# print(sorted([x.split(sep)[-1] for x in daily if x not in all_sources]))
# print(sorted([x.split(sep)[-1] for x in all_sources]))

print("Write cleaned files to new dir")
for source in tqdm(all_sources):
    f = open(source, 'r', errors="ignore")
    data = f.read().strip()
    f.close()

    with open(join(DIR_FILTER, source.split(sep)[-1]), 'w', errors="ignore") as out:
        out.write(data)


# similar = []
# for x in tqdm(ismdb):
#     x = x.split('.txt')[0]
#     for y in daily:
#         y = y.split('.txt')[0]
#         result = fuzz.ratio("".join(x.split("-")).lower(),
#                             "".join(y.split("-")).lower())
#         if result > 98:
#             similar.append((x,y))


# print(similar)
# print(len(similar))

# same = []

# for (x,y) in tqdm(similar):
#     ismdb_f = open(join(DIR_ISMDB, x + '.txt'), 'r', errors="ignore")
#     ismdb_file = ismdb_f.read(5000)
#     ismdb_file = re.sub(r'\n+', '\n', ismdb_file).strip()
#     ismdb_f.close()

#     daily_f = open(join(DIR_DAILY, y + '.txt'), 'r', errors="ignore")
#     daily_file = daily_f.read(5000)
#     daily_file = re.sub(r'\n+', '\n', daily_file).strip()
#     daily_f.close()

#     if fuzz.ratio(ismdb_file.lower(), daily_file.lower()) > 60:
#         same.append((x, y))

# # print(same)
# not_matched = [x for x in similar if x not in same]
# print(not_matched)
# print(len(not_matched))

