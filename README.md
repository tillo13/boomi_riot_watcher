# League of Legends ARAM Sabermetric Stats Enhancer (L.L.A.S.S.E?)

The project consists of a handful (more coming as fun) Python scripts.  You're welcome to tear them all apart.  I'm a mediocre player, so have mediocre results, but enjoy ARAM only, so they're all based on that.  These Python scripts are used to fetch, analyze, and visualize League of Legends ARAM match data. They can retrieve and analyze match data, generate detailed statistics about summoners and champions, and create a table that shows the win percentages of different combinations of players.

## Outline of the Scripts

1. `PROD_RunMe1st_riot_lol_query_any_number_user_save_json.py`: This script is used to retrieve match data from the Riot Games API and save this data to local JSON files. The script first retrieves the summoner names and the Riot API key from environment variables. It then fetches data for each summoner and for each match where the summoner participated. The match data is saved to a JSON file located in a directory specific to the summoner.

2. `PROD_summoner_stats_per_champion.py`: This script analyzes the match data previously retrieved and creates a table with detailed statistics about each summoner and champion. The script traverses a directory tree where each directory is named for a summoner and contains the match data files for that summoner. The summoned data and the champion data are classified and various counts and averages are calculated (e.g., average damage dealt, total kills & deaths, etc.).

3. `PROD_riot_lol_wins_perc_by_group.py`: This script analyzes the match data previously retrieved and generates a table that shows the win percentages for all combinations of players specified. It scans the JSON match data files looking for matches where the specified summoners were participating. It then calculates win percentages and prints a table sorted by win percentage in descending order.

## Installation and setup:

1. Download and Install Python

   - This project requires Python 3 and is tested with Python 3.9.
   - Download link and instructions are available here: https://www.python.org/downloads/

2. Clone this repository, navigate into the project directory.

3. Install Packages

   - Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required packages.

   ```bash
   pip install python-dotenv riotwatcher tabulate numpy termcolor pytz
   ```

4. Insert your RIOT API Key in the .env file.

   - Create an application in the [Riot Developer portal](https://developer.riotgames.com/) and generate an API key.
   - Create a .env file in the project root and add the API key to it like so:

   ```bash
   RIOT_API_KEY='your-api-key-goes-here'
   ```

5. Provide summoner(s) you'd like to analyze in the .env file. 

   - Add the Summoners like so:

   ```bash
   PLAYERS='summoner1,summoner2'
   ```

## Running the scripts:

Each script can be run from the command line by navigating into the script's directory and executing the script with Python. For example:

- Fetch data:

```bash
python PROD_RunMe1st_riot_lol_query_any_number_user_save_json.py
```

- Generate summoner & champion stats:

```bash
python PROD_summoner_stats_per_champion.py
```

- Generate win percentages table:

```bash
python PROD_riot_lol_wins_perc_by_group.py
```
## Note:

This project uses the [RiotWatcher](https://riot-watcher.readthedocs.io/en/latest/) library to access the Riot Games API. According to the documentation of that library, requests to the Riot Games API are rate limited to 20 requests every 1 second and 100 requests every 2 minutes. These scripts don't implement any means to prevent exceeding this rate limit.

The access to the Riot Games API is subject to the [Riot Games Developer Terms of Service](https://developer.riotgames.com/terms-of-service.html). Please ensure you read and understand these terms before you start fetching data from the API. 

The Riot Games API can provide data from various regions. A region is set in the first script (`prod]RunMe1st_riot_lol_query_any_number_user_save_json.py`). By default, this is set as `'na1'` (North America). If you wish to gather data from a different region, make sure you modify that variable to your desired region according to the Riot API regional endpoints detailed in Riot API documentation.

If you are not providing your summoner(s) via the environment variable `PLAYERS`, add your summoners to the list of `players` in `PROD_riot_lol_wins_perc_by_group.py`.


## Potential Enhancements:

- Implement a means to honor the rate limits imposed by the Riot Games API.
- Add error checking to ensure the Riot Games API key is provided and that it is a valid key.
- Add support to gather data from more than one region concurrently.
- Improve parsing and calculation performance by optimizing data structures and algorithms used.
- Add the ability to exclude certain match data from the result. This can be helpful if you want to focus on recent data, or if you had a very bad day and fed horribly in all matches :)
- Writes data directly to a Structured Query Language (SQL) database or NoSQL database for more robust data handling.

##example outputs: 
For PROD_RunMe1st_riot_lol_query_any_number_user_save_json.py, the output appears as follows:

```
Number of users to process: 5
[Now] user1: [Valid user!] Last logged match: 2022-April-12_1748! Processing... (1/5)
```

For PROD_riot_lol_wins_perc_by_group.py, the following output may be given:

```
Win %    Total Games    Total Wins    Total Losses    First Played              Last Played              Last Match Id    Player Combination
-------  -------------  ------------  --------------  ------------------------  -----------------------  ---------------  -------------------------------------
54.93%   304            167           137             2021-June-30_104248       2023-June-08_173944      NA1_4678394439   Joeyjoejoe, Bobbybobbob
51.46%   274            141           133             2021-January-22_122733    2023-June-26_174954      NA1_4695645856   Jimmyjimjim, Bobbybobbob
50.00%   10             5             5               2023-June-08_085204       2023-June-28_131835      NA1_4697320513   Jimmyjimjim, Bobbybobbob, Joeyjoejoe
49.04%   989            485           504             2022-September-23_083319  2023-July-02_092607      NA1_4701030962   Joeyjoejoe
```
For the PROD_summoner_stats_per_champion.py example, the following output may be generated:

```
Summoner     Champ           Match Count    Avg KDA    Kills    Deaths    Assists    DoubleKs    TripleKs    QuadraKs    PentaKs    Max kSpree    Avg dmg Dealt    Max Kills  Last Match Played As
-----------  ------------  -------------  ---------  -------  --------  ---------  ----------  ----------  ----------  ---------  ------------  ---------------  -----------  ------------------------
Joeyjoejoe   Karthus                  46      2.861      408       642       1367           1           1           3          6            23            20277           19  2023-July-01_075445
Bobbybobbob  Chogath                  40      3.804      323       358        907           1           5           3          2            24            20095           28  2023-June-29_202434
Jimmyjimjim  FiddleSticks             40      3.829      296       377        964           0           2           9          2            31            17695           14  2023-July-02_092607
``` 

These examples illustrate how the scripts might present output based on the function performed by each script.  There's more, but creating this readme with chatGPT, I've run out of tokens, soooo, I'll just stop here.  Feel free to use for whatever reason.  MIT licensed, so do what you'd like!