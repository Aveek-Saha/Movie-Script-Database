import os
import json
import glob
from pathlib import Path
from tqdm import tqdm

WRITE_DIR = 'scripts/occurances/'
if not os.path.exists(WRITE_DIR):
    os.makedirs(WRITE_DIR)

for filename in tqdm(glob.glob('scripts/parsed/dialogue/*.txt')):
   with open(os.path.join(os.getcwd(), filename), 'r', encoding='utf-8') as f:
       words = dict()
       for line in f:
           dialogue = line.split(">",1)[1].lower()
           for word in dialogue.split(" "):
               if (word):
                   list_of_chars = ['(', ')', '.', '\n', '\"', '!', '?']
                   for char in list_of_chars:
                      word = word.replace(char,'')
                   if (word in words):
                       words[word] += 1
                   else:
                       words[word] = 1
       sorted_words = dict(sorted(words.items(), key=lambda item: item[1]))
       clean_filename = Path(filename).stem
       clean_filename = clean_filename.replace('_dialogue', '')
       with open(WRITE_DIR+clean_filename+'.json', 'w') as json_file:
           json.dump(sorted_words, json_file, indent=4, separators=(',',':'))
