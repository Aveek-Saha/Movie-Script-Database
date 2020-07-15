# The Movie Script Database
This is an utility that allows you to collect movie scripts from several sources and create a database of ~2.3k movie scripts as `.txt` files along with the metadata for the movies.
 
**This is still a work in progress so stay tuned for updates.**
 
There are three steps to the whole process:
1. Collect data from various sources - Scrape websites for scripts in HTML, txt, doc or pdf format
2. Remove duplicates from different sources - Automatically remove as many duplicates from different sources as possible
3. Collect metadata - Get metadata about the scripts for additional processing
4. Parse Scripts - Convert scripts into lines with just Character => dialogue
 
## Instructions for use
1. Install all dependencies using `pip install -r requirements.txt`.
2. Collect all the scripts: `python get_scripts.py`. This might take a while(2+ hrs).
3. Remove duplicates and empty files: `python clean_files.py`.
4. Collect metadata from TMDb and OMDb: `python get_metadata.py`.
5. Parse scripts: `python parse_files.py`.
 
The sources that scripts are collected from are:
- [IMSDb](https://www.imsdb.com/)
- [Dailyscript](https://www.dailyscript.com/)
- [Awesomefilm](http://www.awesomefilm.com/)
- [Weeklyscript](https://www.weeklyscript.com/)
- [Scriptsavanat](https://thescriptsavant.com/)
- [Screenplays online](https://www.screenplays-online.de/)
- [Scripts for you](https://sfy.ru/)
 
The script for parsing the movie scripts come from this paper: `Linguistic analysis of differences in portrayal of movie characters, in: Proceedings of Association for Computational Linguistics, Vancouver, Canada, 2017` and the code can be found here: https://github.com/usc-sail/mica-text-script-parser