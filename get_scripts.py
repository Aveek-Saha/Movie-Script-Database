import sources

import json

f = open('sources.json','r')
data = json.load(f)

for source in data:
    print("Fetching scripts from %s" % (source))
    included = data[source]
    if source == "imsdb" and included == "true":
        sources.get_imsdb()
    elif source == "screenplays" and included == "true":
        sources.get_screenplays()
    elif source == "scriptsavant" and included == "true":
        sources.get_scriptsavant()
    elif source == "weeklyscript" and included == "true":
        sources.get_weeklyscript()
    elif source == "dailyscript" and included == "true":
        sources.get_dailyscript()
    elif source == "awesomefilm" and included == "true":
        sources.get_awesomefilm()
    elif source == "sfy" and included == "true":
        sources.get_sfy()
    elif source == "scriptslug" and included == "true":
        sources.get_scriptslug()
    
    print()

