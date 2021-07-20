# The Movie Script Database
This is an utility that allows you to collect movie scripts from several sources and create a database of 2.5k+ movie scripts as `.txt` files along with the metadata for the movies.
 
There are three steps to the whole process:
1. Collect data from various [sources](https://github.com/Aveek-Saha/Movie-Script-Database#sources) - Scrape websites for scripts in HTML, txt, doc or pdf format
2. Remove duplicates from different sources - Automatically remove as many duplicates from different sources as possible
3. Collect metadata - Get metadata about the scripts for additional processing
4. Parse Scripts - Convert scripts into lines with just Character => dialogue
 
# Usage

## Dependencies
Read the instructions for installing `textract` first [here](https://textract.readthedocs.io/en/stable/installation.html).

Then install all dependencies using pip
```
pip install -r requirements.txt
```

## Collect movie scripts

Modify the sources you want to download in `sources.json`. If you want a source to be included, set the value to `true`, or else set it as `false`.

Collect all the scripts from the sources listed below: 
```
python get_scripts.py
```

* This might take a while(4+ hrs) depending on your network connection.
* The script takes advantage of parallel processing to speed up the download process.
* If there are missing/incomplete downloads, the script will only attempt to download the missing scripts.
* In case of scripts in PDF or DOC format, the original file is stored in the `temp` directory.

## Collect metadata

Collect metadata from TMDb and IMDb: 
```
python get_metadata.py
```

You'll need an API key for using the TMDb api and you can find out more about it here. Once you get the API key it has to be stored in a file called `config.py` in this format:

```py
tmdb_api_key = "<Your API key>" 
```
This step will also combine duplicates, and your final metadata will be in this format:

```json
{
    "uniquescriptname": {
        "files": [
            {
                "name": "Duplicate 1",
                "source": "Source of the script",
                "file_name": "name of the file",
                "script_url": "Original link to script",
                "size": "size of file"
            },
            {
                "name": "Duplicate 2",
                "source": "Source of the script",
                "file_name": "name of the file",
                "script_url": "Original link to script",
                "size": "size of file"
            }
        ],
        "tmdb": {
            "title": "Title from TMDb",
            "release_date": "Date released",
            "id": "TMDb ID",
            "overview": "Plot summary"
        },
        "imdb": {
            "title": "Title from IMDb",
            "release_date": "Year released",
            "id": "IMDb ID"
        }
    }
}
```

<!-- 3. Remove duplicates and empty files: `python clean_files.py`.
5. Parse scripts: `python parse_files.py`. -->

# Sources

### Metadata:

- [TMDb](https://www.themoviedb.org/)
- [IMDb](https://www.imdb.com/)

### Scripts:

- [IMSDb](https://www.imsdb.com/)
- [Dailyscript](https://www.dailyscript.com/)
- [Awesomefilm](http://www.awesomefilm.com/)
- [Scriptsavanat](https://thescriptsavant.com/)
- [Screenplays online](https://www.screenplays-online.de/)
- [Scripts for you](https://sfy.ru/)
- [Script Slug](https://www.scriptslug.com/)
- [Actor Point](https://www.actorpoint.com/)
- [Script PDF](https://scriptpdf.com/)

**Note:**
- [~~Weeklyscript~~](https://www.weeklyscript.com/) (Site no longer active)
 
The script for parsing the movie scripts come from this paper: `Linguistic analysis of differences in portrayal of movie characters, in: Proceedings of Association for Computational Linguistics, Vancouver, Canada, 2017` and the code can be found here: https://github.com/usc-sail/mica-text-script-parser
