# This script analyzes riot league match data json files to determine the performance of two specific players.
# It requires the following dependencies: os, json.
import os
import json

match_dir = os.path.expanduser('matches')  # the directory to crawl
players = ['user1', 'user2']
players = [player.lower() for player in players]  # convert to lowercase to handle odd capitalizations

games_played_together = 0  # initialize a counter for games played together
wins_together = 0
losses_together = 0  # initialize a counter for losses together
error_count = 0  # initialize a counter for files with errors
visited_matches = set()  # track visited matches
duplicate_match_count = 0  # initialize a counter for duplicate matches

# Walk through all the folders and files in the match directory
for root, dirs, files in os.walk(match_dir):
    for filename in files:
        if filename.endswith('.json'):  # if current file is a json file
            try:
                match = json.load(open(os.path.join(root, filename), 'r'))
                match_id = match['metadata']['matchId']

                if match_id in visited_matches:
                    duplicate_match_count += 1
                else:
                    visited_matches.add(match_id)

                    playing_players = []  # initialize list to store names of those players who played this match and are in the list
                    win_status = []  # initialize list to store win status of players

                    for participant in match['info']['participants']:
                        summoner_name = participant['summonerName'].lower()
                        if summoner_name in players:  # check if participant is one of the players
                            if summoner_name not in [name.lower() for name in ['jakethetall', 'anonobot']]:
                                playing_players.append(summoner_name)
                                win_status.append(participant['win'])

                    # check if both players are in the match
                    if all(player in playing_players for player in players):
                        games_played_together += 1
                        # check if both players have the same win status
                        if win_status.count(True) == 2:
                            wins_together += 1
                        elif win_status.count(False) == 2:
                            losses_together += 1
            except json.JSONDecodeError:
                error_count += 1  # increment the error count if a json load operation fails

win_ratio_together = (wins_together / games_played_together) * 100 if games_played_together else 0

print(f"player1/player2 played together in {games_played_together} games.")
print(f"They won {wins_together} games when playing together.")
print(f"They lost {losses_together} games when playing together.")
print(f"Their win ratio when playing together is {win_ratio_together}%.")
print(f"{duplicate_match_count} duplicate matches were found.")
print(f"{error_count} file(s) were skipped due to errors.")
