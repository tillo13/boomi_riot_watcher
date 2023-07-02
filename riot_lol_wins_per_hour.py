import os
import json
from datetime import datetime
import pytz
from tabulate import tabulate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the players from the environment variable
players_str = os.getenv('PLAYERS')
players = players_str.split(',') if players_str is not None else []

#players = ['put_user', 'more users', 'even_more']
players = [player.lower() for player in players]
match_dir = os.path.expanduser('matches')

wins_by_hour = {player: {hour: 0 for hour in range(24)} for player in players}
losses_by_hour = {player: {hour: 0 for hour in range(24)} for player in players}
games_by_hour = {player: {hour: 0 for hour in range(24)} for player in players}

error_count = 0
handled_matches = {}

for root, dirs, files in os.walk(match_dir):
    for filename in files:
        if filename.endswith('.json'):
            try:
                match = json.load(open(os.path.join(root, filename), 'r'))

                if 'metadata' not in match:
                    print("Skipping match due to missing 'metadata'")
                    continue
                match_id = match['metadata']['matchId']

                if match_id in handled_matches:
                    continue

                utc_time = datetime.fromtimestamp(match['info']['gameCreation'] / 1000)
                seattle_tz = pytz.timezone('America/Los_Angeles')
                creation_time = utc_time.astimezone(seattle_tz)
                
                for participant in match['info']['participants']:
                    
                    player_name = participant['summonerName'].lower()
                    
                    if player_name in players:
                        game_hour = creation_time.hour
                        games_by_hour[player_name][game_hour] += 1

                        if participant['win']:
                            wins_by_hour[player_name][game_hour] += 1
                        else:
                            losses_by_hour[player_name][game_hour] += 1

                handled_matches[match_id] = True
                
            except json.JSONDecodeError:
                error_count += 1

total_wins_by_hour = {hour: sum(wins_by_hour[player][hour] for player in players) for hour in range(24)}
total_losses_by_hour = {hour: sum(losses_by_hour[player][hour] for player in players) for hour in range(24)}
total_games_by_hour = {hour: sum(games_by_hour[player][hour] for player in players) for hour in range(24)}

table_data = []
for hour in range(24):
    games = total_games_by_hour[hour]
    if games > 0:
        win_ratio = (total_wins_by_hour[hour] / games) * 100
        loss_ratio = (total_losses_by_hour[hour] / games) * 100
        hour_str = f"{hour % 12 if hour % 12 > 0 else 12}{'am' if hour < 12 else 'pm'}"
        table_data.append([
            hour_str,
            '{0:.2f}%'.format(win_ratio),
            '{0:.2f}%'.format(loss_ratio),
            games,
            total_wins_by_hour[hour],
            total_losses_by_hour[hour],
        ])

table_data.sort(key=lambda row: row[1], reverse=True)

print(tabulate(table_data, headers=['Hour of Day', 'Win %', 'Loss %', 'Total Games', 'Total Wins', 'Total Losses'], tablefmt='simple', numalign="left"))