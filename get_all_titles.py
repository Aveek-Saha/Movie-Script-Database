import os
import json
from tqdm import tqdm

with open(os.path.join(os.getcwd(), 'scripts/metadata/clean_parsed_meta.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
    titles = dict()
    for movie in data.items():
        name = movie[1]['file']['name']
        titles[name] = name.replace(' ', '-')+'.json'
    with open('all_titles.json', 'w') as json_file:
        json.dump(titles, json_file, indent=4, separators=(',',':'))
