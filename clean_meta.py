from os import dup, listdir, makedirs
from os.path import isfile, join, sep, getsize, exists

import re
import json
import string

f = open('sources.json', 'r')
data = json.load(f)

META_DIR = join("scripts", "metadata")

metadata = {}
for source in data:
    included = data[source]
    meta_file = join(META_DIR, source + ".json")
    if included == "true" and isfile(meta_file):
        with open(meta_file) as json_file:
            source_meta = json.load(json_file)
            metadata[source] = source_meta

forbidden = ["the", "a", "an", "and", "or", "part",
             "vol", "chapter", "movie", "transcript"]
unique = []
origin = {}
for source in metadata:
    DIR = join("scripts", "unprocessed", source)
    files = [join(DIR, f) for f in listdir(DIR) if isfile(
        join(DIR, f)) and getsize(join(DIR, f)) > 3000]
    
    source_meta = metadata[source]
    for script in source_meta:
        name = re.sub(r'\([^)]*\)', '', script.strip()).lower()
        name = " ".join(name.split('-'))
        name = re.sub(r'['+string.punctuation+']', ' ', name)
        name = re.sub(' +', ' ', name).strip()
        name = name.split()
        name = " ".join(list(filter(lambda a: a not in forbidden, name)))
        name = "".join(name.split())
        unique.append(name)
        if name not in origin:
            origin[name] = []
        curr_script = metadata[source][script]
        curr_file = join("scripts", "unprocessed", source, curr_script["file_name"] + ".txt") 
        
        if curr_file in files:
            file_info = {
                source: {
                        "name": script,
                        "file_name": curr_script["file_name"],
                        "script_url": curr_script["script_url"],
                        "size": getsize(curr_file)
                    }
                }
            origin[name].append(file_info)

final = sorted(list(set(unique)))
# print(final)
# print(len(final))

with open(join(META_DIR, "clean_meta.json"), "w") as outfile:
    json.dump(origin, outfile, indent=4)

print(len(origin))

# for script in final:
#     print(origin[script])
