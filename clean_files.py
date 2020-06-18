from fuzzywuzzy import fuzz
from os import listdir
from os.path import isfile, join
from tqdm import tqdm
import re

DIR_ISMDB = join("scripts", "ismdb")
DIR_DAILY = join("scripts", "dailyscript")

ismdb = [f for f in listdir(DIR_ISMDB) if isfile(join(DIR_ISMDB, f))]
daily = [f for f in listdir(DIR_DAILY) if isfile(join(DIR_DAILY, f))]

# print(ismdb)
similar = []
for x in tqdm(ismdb):
    x = x.split('.txt')[0]
    for y in daily:
        y = y.split('.txt')[0]
        result = fuzz.ratio("".join(x.split("-")).lower(),
                            "".join(y.split("-")).lower())
        if result > 98:
            similar.append((x,y))

print(similar)
print(len(similar))

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

