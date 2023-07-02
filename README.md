# League of Legends ARAM Sabermetric Stats Enhancer (L.L.A.S.S.E?)

This python script is used to fetch and calculate several individual statistics, overall statistics, and rank grades based on these statistics, from ARAM (All Random All Mid) matches played in the game League of Legends (LoL) using the Riot Games API.

This script requires the following environment variable to be set up:

- `RIOT_API_KEY` - Your Riot Games API key which can be obtained from [Riot's Developer Portal](https://developer.riotgames.com/). The API key is required to fetch the match data from Riot's servers.

# Features

- Fetch ARAM matches data from the Riot Games API.
- Calculate a various of individual game metrics, including:
  - Kill, death and assist ratios.
  - Damage dealt per minute.
  - Gold earned per minute.
  - Percentage of team's overall damage dealt.
  - Percentage of team's overall damage taken.
- Determine a "total rank score" based on aforementioned calculated metrics.
- Assign a grade (ranging from D- to S+) based on the "total rank score".
- Calculate and display overall statistics across all queried matches.
- Generate a comprehensive report for each match, including the match details, individual and overall stats, rank score and grade.
- Save the data fetched to JSON files.
  
# How to use

Set up the `RIOT_API_KEY` as an environment variable in your system. 
Then, run `python riot_lol_query_matches_save_json.py`.  This saves all the files to your local machine as JSON files, in a "matches" directory.

Replace `'username'` in the script with your Summoner Name to fetch your own ARAM matches data.

You can modify options such as:

- `debug_mode`: Set to `True` to print calculation details, `False` hides them.
- `KDA_WEIGHT`: Modify this value to tweak the weight the KDA has on the total rank score.

# Dependencies

The script requires the external libraries mentioned at the top of the script to be installed in your Python environment.

# Output

The script will generate a JSON file for each match. It will also print to console match statistics, overall statistics, individual game statistics along with a rank score and its corresponding grade.

The JSON files will be stored in a folder named "matches" in the same directory of the script, and in a subfolder named with your summoner's name in lowercase and replacing spaces with underscores.

Additionally, the script also calls another python script named `json_to_csv.py` that is supposed to convert the generated JSON files to a CSV file.

-------------------

**NOTE**: This script does not include exception handling for incorrect API keys, summoner names, or exceeded API call limits. The script will crash if encounters an API error. Also, to protect your API key and prevent unauthorized usage, do not publish it.


# JSON to CSV Converter - `json_to_csv.py`

This additional python script, `json_to_csv.py`, is used to convert multiple JSON files fetched by the main script that derive from Riot Games API data of League of Legends ARAM matches into a single CSV file.

## Features

- Convert multiple JSON files into a single CSV file.
- Handle nested JSON objects and lists by flattening them into a single level depth.
- Handle exceptions and print the respective error message.
- Optional to set a custom filename for the output CSV file and to specify a specific user's matches data to fetch from. 

## How to use

This script is automatically called at the end of the main script. If you want to run this script manually, you can run `python3 json_to_csv.py your_csv_filename your_summoner_name`, replacing 'your_csv_filename' with the desired name for the output CSV file and 'your_summoner_name' with the Summoner Name whose matches data you wish to convert. If no arguments are provided, the script will run with the default options.

## Dependencies

This script requires the pandas, os, json and datetime modules to be pre-installed in your Python environment.

## Output

The script generates a CSV file with the same data from the JSON files. The CSV file will be stored in the same user's subfolder inside the "matches" directory. The name of the file can be set with an argument when running the script, otherwise it will be named "default.csv".

Upon completion, the script will print a success message, specifying the name and the location of the generated CSV file.

**NOTE**: This script does not include exception handling for nonexistent directories, improperly formatted JSON files, or CSV write errors. The script will crash if encounters such errors.