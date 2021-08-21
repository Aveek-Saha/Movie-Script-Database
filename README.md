# The Movie Script Database

This is an utility that allows you to collect movie scripts from several sources and create a database of 2.5k+ movie scripts as `.txt` files along with the metadata for the movies.

There are four steps to the whole process:

1. Collect scripts from various [sources](https://github.com/Aveek-Saha/Movie-Script-Database#sources) - Scrape websites for scripts in HTML, txt, doc or pdf format
1. Collect metadata - Get metadata about the scripts from [TMDb](https://www.themoviedb.org/) and [IMDb](https://www.imdb.com/) for additional processing
1. Find duplicates from different sources - Automatically group and remove duplicates from different sources.
1. Parse Scripts - Convert scripts into lines with just Character and dialogue

## Usage

The following steps MUST be run in order

### Clone

Clone this repository:

```
git clone https://github.com/Aveek-Saha/Movie-Script-Database.git
cd Movie-Script-Database
```

### Dependencies

Read the instructions for installing `textract` first [here](https://textract.readthedocs.io/en/stable/installation.html).

Then install all dependencies using pip

```
pip install -r requirements.txt
```

### Collect movie scripts

Modify the sources you want to download in `sources.json`. If you want a source to be included, set the value to `true`, or else set it as `false`.

```
python get_scripts.py
```

Collect all the scripts from the sources listed below:

```json
{
    "imsdb": "true",
    "screenplays": "true",
    "scriptsavant": "true",
    "dailyscript": "true",
    "awesomefilm": "true",
    "sfy": "true",
    "scriptslug": "true",
    "actorpoint": "true",
    "scriptpdf": "true"
}
```

-   This might take a while (4+ hrs) depending on your network connection.
-   The script takes advantage of parallel processing to speed up the download process.
-   If there are missing/incomplete downloads, the script will only download the missing scripts if run again.
-   In case of scripts in PDF or DOC format, the original file is stored in the `temp` directory.

### Collect metadata

Collect metadata from TMDb and IMDb:

```
python get_metadata.py
```

You'll need an API key for using the TMDb api and you can find out more about it [here](https://www.themoviedb.org/documentation/api). Once you get the API key it has to be stored in a file called `config.py` in this format:

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
                "file_name": "name-of-the-file",
                "script_url": "Original link to script",
                "size": "size of file"
            },
            {
                "name": "Duplicate 2",
                "source": "Source of the script",
                "file_name": "name-of-the-file",
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

### Remove duplicates

Run:

```
python clean_files.py
```

This will remove the duplicate files as best as possible without false positives. In the end, the files will be stored in the `scripts\filtered` directory.

A new metadata file is created where only one file exists for each unique script name, in this format:

```json
{
    "uniquescriptname": {
        "file": {
            "name": "Movie name from source",
            "source": "Source of the script",
            "file_name": "name-of-the-file",
            "script_url": "Original link to script",
            "size": "size of file"
        },
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

The scripts are also cleaned to remove as much formatting weirdness that comes from using OCR to read from a PDF as possible.

### Parse Scripts

Run:

```
python parse_files.py
```

This will parse your non duplicate scripts from the previous step. The parsed scripts are put into three folders

-   `scripts/parsed/tagged`: Contains scripts where each line has been tagged. The tags are
    -   `S` = Scene
    -   `N` = Scene description
    -   `C` = Character
    -   `D` = Dialogue
    -   `E` = Dialogue metadata
    -   `T` = Transition
    -   `M` = Metadata
-   `scripts/parsed/dialogue`: Contains scripts where each line has the character name, followed by a dialogue, in this format, `C=>D`
-   `scripts/parsed/charinfo`: Contains a list of each character in the script and the number of lines they have, in this format, `C: Number of lines`

A new metadata file is created with the following format:

```json
{
    "uniquescriptname": {
        "file": {
            "name": "Movie name from source",
            "source": "Source of the script",
            "file_name": "name-of-the-file",
            "script_url": "Original link to script",
            "size": "size of file"
        },
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
        },
        "parsed": {
            "dialogue": "name-of-the-file_dialogue.txt",
            "charinfo": "name-of-the-file_charinfo.txt",
            "tagged": "name-of-the-file_parsed.txt"
        }
    }
}
```

## Directory structure

After running all the steps, your folder structure should look something like this:

```
scripts
│
├── unprocessed // Scripts from sources
│   ├── source1
│   ├── source2
│   └── source3
│
├── temp // PDF files from sources
│   ├── source1
│   ├── source2
│   └── source3
│
├── metadata // Metadata files from sources/cleaned metadata
│   ├── source1.json
│   ├── source2.json
│   ├── source3.json
│   └── meta.json
│
├── filtered // Scripts with duplicates removed
│
└── parsed // Scripts parsed using the parser
    ├── dialogue
    ├── charinfo
    └── tagged
```

## Sources

### Metadata:

-   [TMDb](https://www.themoviedb.org/)
-   [IMDb](https://www.imdb.com/)

### Scripts:

-   [IMSDb](https://www.imsdb.com/)
-   [Dailyscript](https://www.dailyscript.com/)
-   [Awesomefilm](http://www.awesomefilm.com/)
-   [Scriptsavanat](https://thescriptsavant.com/)
-   [Screenplays online](https://www.screenplays-online.de/)
-   [Scripts for you](https://sfy.ru/)
-   [Script Slug](https://www.scriptslug.com/)
-   [Actor Point](https://www.actorpoint.com/)
-   [Script PDF](https://scriptpdf.com/)

**Note:**

-   [~~Weeklyscript~~](https://www.weeklyscript.com/) (Site no longer active)


## Citing

If you use The Movie Script Database, please cite:

```
@misc{Saha_Movie_Script_Database_2021,
    author = {Saha, Aveek},
    month = {7},
    title = {{Movie Script Database}},
    url = {https://github.com/Aveek-Saha/Movie-Script-Database},
    year = {2021}
}
```

## Credits

The script for parsing the movie scripts come from this paper: `Linguistic analysis of differences in portrayal of movie characters, in: Proceedings of Association for Computational Linguistics, Vancouver, Canada, 2017` and the code can be found here: https://github.com/usc-sail/mica-text-script-parser
