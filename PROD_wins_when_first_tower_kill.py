import os
import json
import itertools
import pytz
from datetime import datetime
from tabulate import tabulate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the players from the environment variable
players_str = os.getenv('PLAYERS')
players = players_str.split(',') if players_str is not None else []

players = [player.lower() for player in players]
match_dir = os.path.expanduser('matches')

error_count = 0
visited_matches = {}
duplicate_matches = {}
processed_combinations = []
matches_processed = 0

player_combinations = []
for r in range(len(players), 0, -1):
    player_combinations.extend(itertools.combinations(players, r))

games_played_together = {combination: 0 for combination in player_combinations}
wins_together = {combination: 0 for combination in player_combinations}
losses_together = {combination: 0 for combination in player_combinations}
first_played = {combination: None for combination in player_combinations}
last_played = {combination: None for combination in player_combinations}
last_match_id = {combination: None for combination in player_combinations}
wins_with_first_tower_kill = {combination: 0 for combination in player_combinations}
losses_with_first_tower_kill = {combination: 0 for combination in player_combinations}
wins_without_first_tower_kill = {combination: 0 for combination in player_combinations}
losses_without_first_tower_kill = {combination: 0 for combination in player_combinations}

handled_matches = {}

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

                if match_id in handled_matches:
                    continue

                utc_time = datetime.fromtimestamp(match['info']['gameCreation'] / 1000)

                seattle_tz = pytz.timezone('America/Los_Angeles')
                creation_time = utc_time.astimezone(seattle_tz)

                match_found = False

                for combination in player_combinations:
                    playing_players = []
                    win_status = []
                    first_tower_kill = []
                    for participant in match['info']['participants']:
                        if participant['summonerName'].lower() in combination:
                            playing_players.append(participant['summonerName'].lower())
                            win_status.append(participant['win'])
                            first_tower_kill.append(participant['firstTowerKill'])

                    if set(playing_players) == set(combination):
                        visited_tuple = (match_id, combination)

                        if visited_tuple in visited_matches:
                            duplicate_matches[combination] = duplicate_matches.get(combination, 0) + 1
                            continue

                        visited_matches[visited_tuple] = True
                        handled_matches[match_id] = True

                        if len(combination) == len(players):
                            processed_combinations.append(combination)

                        if not first_played[combination] or creation_time < first_played[combination]:
                            first_played[combination] = creation_time
                        if not last_played[combination] or creation_time > last_played[combination]:
                            last_played[combination] = creation_time
                            last_match_id[combination] = match_id

                        games_played_together[combination] += 1
                        if win_status.count(True) == len(combination):
                            wins_together[combination] += 1
                            if first_tower_kill.count(True) == len(combination):
                                wins_with_first_tower_kill[combination] += 1
                            else:
                                wins_without_first_tower_kill[combination] += 1
                        elif win_status.count(False) == len(combination):
                            losses_together[combination] += 1
                            if first_tower_kill.count(False) == len(combination):
                                losses_with_first_tower_kill[combination] += 1
                            else:
                                losses_without_first_tower_kill[combination] += 1

                        match_found = True
                        break

                if match_found:
                    continue

            except json.JSONDecodeError:
                error_count += 1

table_data = []
for combination in player_combinations:
    games = games_played_together[combination]
    if games > 0:
        win_ratio_together = (wins_together[combination] / games) * 100
        table_data.append([
                '{0:.2f}%'.format(win_ratio_together),
                games,
                wins_together[combination],
                wins_with_first_tower_kill[combination],
                wins_without_first_tower_kill[combination],
                losses_together[combination],
                losses_with_first_tower_kill[combination],
                losses_without_first_tower_kill[combination],
                ', '.join([player.title() for player in combination])
            ])

# ...
print(f"\nDESCRIPTION: This analyzes all ARAM matches and deduces when specific summoners get firstTowerKill.\n")

table_data.sort(key=lambda row: float(row[0].strip('%')), reverse=True)

headers = ['Win %', 'Total Matches', 'Total Wins', 'Win=TRUE|1TK=TRUE', 'Win=TRUE|1TK=FALSE', 'Total Losses','Win=FALSE|1TK=TRUE', 'Win=FALSE|1TK=FALSE', 'Player Combination']
formatted_data = []
for i, row in enumerate(table_data):
    if i % 2 == 1:
        formatted_data.append([f"\033[1m{cell}\033[0m" for cell in row])  # Bold formatting for odd lines
    else:
        formatted_data.append(row)

print(tabulate(formatted_data, headers=headers, tablefmt='simple', numalign="left"))
# ...
print(f"\nLOGGING DATA:")
print(f"{error_count} file(s) were skipped due to errors.")
print(f"Total files scanned: {len(files)}")
total_processed_matches = sum(games_played_together.values())
player_counts = []
for i in range(len(players), 0, -1):
    combinations_of_i = list(itertools.combinations(players, i))
    count = sum(games_played_together[combo] for combo in combinations_of_i)
    player_counts.append(f'{i} players = {count}')