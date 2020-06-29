# The Movie Script Database
This is an utility that allows you to collect movie scripts from several sources and create a database of ~2.5k movie scripts as `.txt` files. The metadata for the movies is also collected automatically.

There are three steps to the whole process:
1. Collect data from various sources
2. Remove duplicates from different sources
3. Get correct metadata about the movies

The sources that scripts are collected from are:
- [IMSDb](https://www.imsdb.com/)
- [Dailyscript](https://www.dailyscript.com/)
- [Awesomefilm](http://www.awesomefilm.com/)
- [Weeklyscript](https://www.weeklyscript.com/)
- [Scriptsavanat](https://thescriptsavant.com/)
- [Screenplays online](https://www.screenplays-online.de/)
- [Scripts for you](https://sfy.ru/)

The script for parsing the movie scripts come from this paper: `Linguistic analysis of differences in portrayal of movie characters, in: Proceedings of Association for Computational Linguistics, Vancouver, Canada, 2017` and the code can be found here: https://github.com/usc-sail/mica-text-script-parser