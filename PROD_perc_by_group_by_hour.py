# Import necessary libraries
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

# Directory where match data files are stored
match_dir = os.path.expanduser('matches')

# List of player names to analyze on your own if you'd like as well
#players = ['statfame','britney phi','anonobot','jakethetall','lilla bryar']
players = [player.lower() for player in players]  # Make all player names lowercase

# Generate player combinations, excluding combinations of fewer than two players
player_combinations = []
for r in range(len(players), 1, -1):  # Change second argument to 1
    player_combinations.extend(itertools.combinations(players, r))

# Initialize counters and containers
error_count = 0
visited_matches = {}
processed_combinations = []
handled_matches = {}

# Initialize data collections for each player combination
wins_by_hour = {combination: {hour: 0 for hour in range(24)} for combination in player_combinations}
losses_by_hour = {combination: {hour: 0 for hour in range(24)} for combination in player_combinations}
games_by_hour = {combination: {hour: 0 for hour in range(24)} for combination in player_combinations}

# Traverse the directory containing match data files
for root, dirs, files in os.walk(match_dir):
    for filename in files:
        if filename.endswith('.json'):  # If the file is a JSON file
            try:
                match = json.load(open(os.path.join(root, filename), 'r'))  # Load match data
                if 'metadata' not in match:
                    print("Skipping match due to missing 'metadata'")
                    continue
                try:
                    match_id = match['metadata']['matchId']
                except KeyError:
                    print("Skipping match due to missing 'matchId' in 'metadata'")
                    continue

                # Skip if match already processed
                if match_id in handled_matches:
                    continue

                # Convert match timestamp to datetime, then to Seattle timezone
                utc_time = datetime.fromtimestamp(match['info']['gameCreation'] / 1000)
                seattle_tz = pytz.timezone('America/Los_Angeles')
                creation_time = utc_time.astimezone(seattle_tz)
                
                match_found = False

                for combination in player_combinations:
                    playing_players = []
                    win_status = []
                    for participant in match['info']['participants']:
                        if participant['summonerName'].lower() in combination:
                            playing_players.append(participant['summonerName'].lower())
                            win_status.append(participant['win'])

                    if set(playing_players) == set(combination):
                        visited_tuple = (match_id, combination)
                        if visited_tuple in visited_matches:
                            continue
                        visited_matches[visited_tuple] = True
                        handled_matches[match_id] = True
                        
                        game_hour = creation_time.hour
                        games_by_hour[combination][game_hour] += 1
                        if win_status.count(True) == len(combination):
                            wins_by_hour[combination][game_hour] += 1
                        elif win_status.count(False) == len(combination):
                            losses_by_hour[combination][game_hour] += 1

                        match_found = True
                        break

                if match_found:
                    continue

            except json.JSONDecodeError:
                error_count += 1

# Prepare to print the table
table_data = []
for combination in player_combinations:
    for hour in range(24):
        games = games_by_hour[combination][hour]
        if games > 0:  # Exclude hours with no games played
            win_ratio = (wins_by_hour[combination][hour] / games) * 100  # Calculate win ratio
            loss_ratio = (losses_by_hour[combination][hour] / games) * 100  # Calculate loss ratio
            hour_str = f"{hour % 12 if hour % 12 > 0 else 12}{'am' if hour < 12 else 'pm'}"
            table_data.append([
                hour_str,
                '{0:.2f}%'.format(win_ratio),
                '{0:.2f}%'.format(loss_ratio),
                games,
                wins_by_hour[combination][hour],
                losses_by_hour[combination][hour],
                ', '.join([player.title() for player in combination])
            ])

# Sort table data by Total Games
table_data.sort(key=lambda row: row[3], reverse=True)

# Print the table
print(tabulate(table_data, headers=['Hour of Day', 'Win %', 'Loss %', 'Total Games', 'Total Wins', 'Total Losses', 'Player Combination'], tablefmt='simple', numalign="left"))