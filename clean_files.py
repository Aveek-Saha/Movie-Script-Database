from fuzzywuzzy import fuzz
from os import listdir
from os.path import isfile, join, sep
from tqdm import tqdm
import re
import itertools

DIR_ISMDB = join("scripts", "ismdb")
DIR_DAILY = join("scripts", "dailyscript")

ismdb = [join(DIR_ISMDB, f) for f in listdir(DIR_ISMDB) if isfile(join(DIR_ISMDB, f))]
daily = [join(DIR_DAILY, f) for f in listdir(DIR_DAILY) if isfile(join(DIR_DAILY, f))]

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
                if len(file_1) >len(file_2):
                    arr.remove(x + '.txt')
                else:
                    arr.remove(y + '.txt')
            except:
                print(x + '.txt', y + '.txt')
                return []

    return arr

print("Remove duplicates from ismdb")
comb_ismdb = list(itertools.combinations(ismdb, 2))
ismdb = remove_duplicates(ismdb, comb_ismdb)
print("Remove duplicates from dailyscript")
comb_daily = list(itertools.combinations(daily, 2))
daily = remove_duplicates(daily, comb_daily)

print("Remove duplicates between sources")
all_sources = ismdb + daily
print(len(all_sources))
comb_all = list(itertools.combinations(all_sources, 2))
all_sources = remove_duplicates(all_sources, comb_all)
print(len(all_sources))

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

