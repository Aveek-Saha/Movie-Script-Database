import sources

import json

f = open('sources.json', 'r')
data = json.load(f)

for source in data:
    included = data[source]
    if included == "true":
        print("Fetching scripts from %s" % (source))
        sources.get_scripts(source=source)
        print()
