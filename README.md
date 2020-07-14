# The Movie Script Database
This is an utility that allows you to collect movie scripts from several sources and create a database of ~2.3k movie scripts as `.txt` files along with the metadata for the movies.

This is still a work in progress so stay tuned for updates.

There are three steps to the whole process:
1. Collect data from various sources - Scrape websites for scripts in HTML, txt, doc or pdf format
2. Remove duplicates from different sources - Automatically remove as many deplicates from different sources as possible
3. Collect metadata - Get metadata about the scripts for additional processing

The sources that scripts are collected from are:
- [IMSDb](https://www.imsdb.com/)
- [Dailyscript](https://www.dailyscript.com/)
- [Awesomefilm](http://www.awesomefilm.com/)
- [Weeklyscript](https://www.weeklyscript.com/)
- [Scriptsavanat](https://thescriptsavant.com/)
- [Screenplays online](https://www.screenplays-online.de/)
- [Scripts for you](https://sfy.ru/)

The script for parsing the movie scripts come from this paper: `Linguistic analysis of differences in portrayal of movie characters, in: Proceedings of Association for Computational Linguistics, Vancouver, Canada, 2017` and the code can be found here: https://github.com/usc-sail/mica-text-script-parser