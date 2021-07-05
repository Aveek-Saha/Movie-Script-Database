from .imsdb import get_imsdb
from .screenplays import get_screenplays
from .scriptsavant import get_scriptsavant
from .weeklyscript import get_weeklyscript
from .dailyscript import get_dailyscript
from .awesomefilm import get_awesomefilm
from .sfy import get_sfy
from .scriptslug import get_scriptslug
from .actorpoint import get_actorpoint
from .scriptpdf import get_scriptpdf
from .utilities import *

def get_scripts(source):
    if source == "imsdb":
        get_imsdb()
    elif source == "screenplays":
        get_screenplays()
    elif source == "scriptsavant":
        get_scriptsavant()
    elif source == "weeklyscript":
        get_weeklyscript()
    elif source == "dailyscript":
        get_dailyscript()
    elif source == "awesomefilm":
        get_awesomefilm()
    elif source == "sfy":
        get_sfy()
    elif source == "scriptslug":
        get_scriptslug()
    elif source == "actorpoint":
        get_actorpoint()
    elif source == "scriptpdf":
        get_scriptpdf()
    else:
        print("Invalid source.")