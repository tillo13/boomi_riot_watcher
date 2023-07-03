import os
import json
import pytz
from datetime import datetime
from tabulate import tabulate
from dotenv import load_dotenv

load_dotenv()

players_str = os.getenv('PLAYERS')
players = players_str.split(',') if players_str is not None else []

players = [player.lower() for player in players]
match_dir = os.path.expanduser('matches')

error_count = 0

games_played = {}  # {('summoner', 'champion'): count}
wins = {}  # {('summoner', 'champion'): count}
losses = {}  # {('summoner', 'champion'): count}
first_match_timestamp = {}  # {('summoner', 'champion'): timestamp}

unique_matches_per_player = {}  # {('summoner'): set(match_id)}
total_matches_analyzed = 0

for root, dirs, files in os.walk(match_dir):
    for filename in files:
        if filename.endswith('.json'):
            try:
                match = json.load(open(os.path.join(root, filename), 'r'))

                if 'metadata' not in match:
                    print(f"Skipping match {filename} due to missing 'metadata'")
                    continue

                try:
                    match_id = match['metadata']['matchId']
                except KeyError:
                    print(f"Skipping match {filename} due to missing 'matchId' in 'metadata'")
                    continue

                for participant in match['info']['participants']:
                    summoner_name = participant['summonerName'].lower()
                    if summoner_name in players:
                        champion_name = participant['championName']

                        player_champion_key = (summoner_name, champion_name)

                        if player_champion_key not in games_played:
                            games_played[player_champion_key] = 0
                            wins[player_champion_key] = 0
                            losses[player_champion_key] = 0
                            first_match_timestamp[player_champion_key] = match['info']['gameCreation']

                        games_played[player_champion_key] += 1
                        if participant['win']:
                            wins[player_champion_key] += 1
                        else:
                            losses[player_champion_key] += 1

                        if summoner_name not in unique_matches_per_player:
                            unique_matches_per_player[summoner_name] = set()

                        unique_matches_per_player[summoner_name].add(match_id)

                        if match['info']['gameCreation'] < first_match_timestamp[player_champion_key]:
                            first_match_timestamp[player_champion_key] = match['info']['gameCreation']

                total_matches_analyzed += 1

            except json.JSONDecodeError:
                error_count += 1

table_data = []
for key in games_played.keys():
    win_percentage = (wins[key] / games_played[key]) * 100
    first_match_time = datetime.fromtimestamp(first_match_timestamp[key] // 1000, tz=pytz.timezone('America/Los_Angeles')).strftime('%Y-%B-%d_%H%M%S')
    table_data.append([key[1], key[0], games_played[key], wins[key], losses[key], win_percentage, first_match_time])

# Sort the table_data by PlayerName (ascending) and TotalGamesWithChampion (descending)
table_data.sort(key=lambda row: (row[1], -row[2]))

headers = ['Champ', 'Summoner', 'TotalGamesWithChamp', 'WinsWithChamp', 'LossesWithChamp', 'Win%', 'FirstLoggedMatch']

print(tabulate(table_data, headers=headers, tablefmt='simple', numalign="left", floatfmt=".2f"))

unique_matches_processed = sum(len(matches) for matches in unique_matches_per_player.values())

print("\nLOGGING DATA:")
print(f"{error_count} file(s) were skipped due to errors.")
print(f"Total files scanned: {len(files)}")
print(f"Unique matches processed: {unique_matches_processed}")
print(f"Total matches analyzed: {total_matches_analyzed}")
