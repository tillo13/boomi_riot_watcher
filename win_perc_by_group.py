# This script analyzes match data json files for a list of league player names.
# It requires the following dependencies: os, json, itertools, pytz, datetime, tabulate.
# The script traverses a directory containing match data files and performs the following tasks:

# Import necessary libraries
import os
import json
import itertools
import pytz
from datetime import datetime
from tabulate import tabulate

# Directory where match data files are stored
match_dir = os.path.expanduser('matches')

# List of player names to analyze
players = ['user1','user2','etc']
players = [player.lower() for player in players]  # Make all player names lowercase for consistency

# Initialize counters and containers
error_count = 0  # Count of how many files have encountered errors during processing
visited_matches = {}  # Matches that have been visited/processed
duplicate_matches = {}  # Matches that are duplicates
processed_combinations = []  # Combinations of players that have been processed
matches_processed = 0  # Count of matches that have been processed

# Generate all possible combinations of players
player_combinations = []
for r in range(len(players), 0, -1):
    player_combinations.extend(itertools.combinations(players, r))

# Initialize data collections for each player combination
games_played_together = {combination: 0 for combination in player_combinations}
wins_together = {combination: 0 for combination in player_combinations}
losses_together = {combination: 0 for combination in player_combinations}
first_played = {combination: None for combination in player_combinations}
last_played = {combination: None for combination in player_combinations}
last_match_id = {combination: None for combination in player_combinations}

# List of already handled matches
handled_matches = {}

# Traverse the directory containing match data files
for root, dirs, files in os.walk(match_dir):
    for filename in files:
        if filename.endswith('.json'):  # If the file is a JSON file
            try:
                # Load match data from the JSON file
                match = json.load(open(os.path.join(root, filename), 'r'))

                # Extract the match ID from the match data
                match_id = match['metadata']['matchId']

                # If the match has already been processed, skip to the next file
                if match_id in handled_matches:
                    continue

                # Convert the game creation timestamp to a datetime object
                utc_time = datetime.fromtimestamp(match['info']['gameCreation'] / 1000)

                # Adjust the datetime object to the desired timezone
                seattle_tz = pytz.timezone('America/Los_Angeles')
                creation_time = utc_time.astimezone(seattle_tz)
                
                # Boolean to check if a match is found
                match_found = False

                # Check each player combination to see if it's present in the match
                for combination in player_combinations:
                    playing_players = []
                    win_status = []
                    for participant in match['info']['participants']:
                        # If the participant is in the combination, add them to the list of playing players
                        if participant['summonerName'].lower() in combination:
                            playing_players.append(participant['summonerName'].lower())
                            win_status.append(participant['win'])

                    # If all the players in the combination were playing in the match
                    if set(playing_players) == set(combination):
                        visited_tuple = (match_id, combination)

                        # Check for duplicates
                        if visited_tuple in visited_matches:
                            duplicate_matches[combination] = duplicate_matches.get(combination, 0) + 1
                            continue

                        # Mark this match-combination as visited
                        visited_matches[visited_tuple] = True
                        handled_matches[match_id] = True

                        # If the full roster was playing, mark this combination as processed
                        if len(combination) == len(players):
                            processed_combinations.append(combination)

                        # Update first and last played times
                        if not first_played[combination] or creation_time < first_played[combination]:
                            first_played[combination] = creation_time
                        if not last_played[combination] or creation_time > last_played[combination]:
                            last_played[combination] = creation_time
                            last_match_id[combination] = match_id

                        # Update game, win, and loss counts
                        games_played_together[combination] += 1
                        if win_status.count(True) == len(combination):
                            wins_together[combination] += 1
                        elif win_status.count(False) == len(combination):
                            losses_together[combination] += 1
                        
                        # Set the match_found to True and break the loop
                        match_found = True 
                        break 

                # If a match was found, continue to the next file
                if match_found:
                    continue

            # If the file cannot be decoded as JSON, increment the error count
            except json.JSONDecodeError:
                error_count += 1

# Prepare table data for tabulation
table_data = []
for combination in player_combinations:
    games = games_played_together[combination]
    if games > 0:  # Exclude combinations with no games played
        win_ratio_together = (wins_together[combination] / games) * 100  # Calculate win ratio
        table_data.append([
            '{0:.2f}%'.format(win_ratio_together),
            games,
            wins_together[combination],
            losses_together[combination],
            first_played[combination].strftime('%Y-%B-%d_%H%M%S') if first_played[combination] else 'N/A',
            last_played[combination].strftime('%Y-%B-%d_%H%M%S') if last_played[combination] else 'N/A',
            last_match_id[combination] if last_match_id[combination] else 'N/A',
            ', '.join([player.title() for player in combination])
        ])

# Sort table data by win ratio
table_data.sort(key=lambda row: float(row[0].strip('%')), reverse=True)

# Print the table
print(tabulate(table_data, headers=['Win %', 'Total Games', 'Total Wins', 'Total Losses', 'First Played', 'Last Played', 'Last Match Id', 'Player Combination'], tablefmt='simple', numalign="left"))

# Print summary information
print(f"\n{error_count} file(s) were skipped due to errors.")
print(f"Total files scanned: {len(files)}")
total_processed_matches = sum(games_played_together.values())
player_counts = []
for i in range(len(players), 0, -1):
    combinations_of_i = list(itertools.combinations(players, i))
    count = sum(games_played_together[combo] for combo in combinations_of_i)
    player_counts.append(f'{i} players = {count}')
print(f"Total matches scanned: {total_processed_matches} ({', '.join(player_counts)})")
