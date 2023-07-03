import json
import os
from datetime import datetime
from scipy.stats import percentileofscore

# Specify the matches folder
matches_folder = "matches"

# Guess the user directory based on the files in the matches folder
user_folder = "statfame"
for file_name in os.listdir(matches_folder):
    if file_name.endswith('.json'):
        user_folder = file_name.split('.')[0]
        break

if user_folder is None:
    print("No JSON files found in the matches folder. Please make sure the first script has run successfully.")
    exit(1)

# Construct the full path of the user folder
user_folder_path = os.path.join(matches_folder, user_folder)

# Start the timestamp at the beginning of the script
start_time = datetime.now()

# Initialize variables for combined totals
total_matches = 0
total_wins = 0
total_kills = 0
total_deaths = 0
total_assists = 0
total_damage_dealt = 0
total_gold_earned = 0
total_game_duration = 0
total_penta_kills = 0
total_quadra_kills = 0
total_triple_kills = 0
total_double_kills = 0
total_skillshots_hit = 0
total_killing_sprees = 0
total_longest_time_spent_living = 0

# Iterate over the JSON files in the user folder
for file_name in os.listdir(user_folder_path):
    if file_name.endswith('.json'):
        file_path = os.path.join(user_folder_path, file_name)
        with open(file_path, 'r') as file:
            match_json = json.load(file)

        # Process the match JSON data
        match_id = match_json['metadata']['matchId']
        participants = match_json['info']['participants']

        print("===============================")
        print(f"Match ID: {match_id}")

        # Iterate over the participants in the match
        for participant in participants:
            # Add the participant's stats to the combined totals
            total_matches += 1
            if participant['win']:
                total_wins += 1
            total_kills += participant['kills']
            total_deaths += participant['deaths']
            total_assists += participant['assists']
            total_damage_dealt += participant['totalDamageDealt']
            total_gold_earned += participant['goldEarned']
            total_game_duration += match_json['info']['gameDuration']
            total_penta_kills += participant.get('pentaKills', 0)
            total_quadra_kills += participant.get('quadraKills', 0)
            total_triple_kills += participant.get('tripleKills', 0)
            total_double_kills += participant.get('doubleKills', 0)
            total_skillshots_hit += participant.get('challenges', {}).get('skillshotsHit', 0)
            total_killing_sprees += participant.get('killingSprees', 0)
            total_longest_time_spent_living += participant.get('longestTimeSpentLiving', 0)

# Calculate the overall averages
average_kills = total_kills / total_matches if total_matches > 0 else 0
average_deaths = total_deaths / total_matches if total_matches > 0 else 0
average_assists = total_assists / total_matches if total_matches > 0 else 0
average_damage_dealt = total_damage_dealt / total_matches if total_matches > 0 else 0
average_gold_earned = total_gold_earned / total_matches if total_matches > 0 else 0
average_game_duration = total_game_duration / total_matches if total_matches > 0 else 0

# Calculate the percentiles
percentile_kills = percentileofscore(range(total_kills + 1), average_kills)
percentile_deaths = percentileofscore(range(total_deaths + 1), average_deaths)
percentile_assists = percentileofscore(range(total_assists + 1), average_assists)
percentile_damage_dealt = percentileofscore(range(total_damage_dealt + 1), average_damage_dealt)
percentile_gold_earned = percentileofscore(range(total_gold_earned + 1), average_gold_earned)
percentile_game_duration = percentileofscore(range(total_game_duration + 1), average_game_duration)

# Print the overall averages and percentiles
print("===============================")
print("Overall Averages and Percentiles")
print(f"Total Matches: {total_matches}")
print(f"Total Wins: {total_wins}")
print(f"Average Kills: {average_kills:.2f} (Percentile: {percentile_kills:.2f}%)")
print(f"Average Deaths: {average_deaths:.2f} (Percentile: {percentile_deaths:.2f}%)")
print(f"Average Assists: {average_assists:.2f} (Percentile: {percentile_assists:.2f}%)")
print(f"Average Damage Dealt: {average_damage_dealt:.2f} (Percentile: {percentile_damage_dealt:.2f}%)")
print(f"Average Gold Earned: {average_gold_earned:.2f} (Percentile: {percentile_gold_earned:.2f}%)")
print(f"Average Game Duration: {average_game_duration:.2f} (Percentile: {percentile_game_duration:.2f}%)")
print(f"Total Penta Kills: {total_penta_kills}")
print(f"Total Quadra Kills: {total_quadra_kills}")
print(f"Total Triple Kills: {total_triple_kills}")
print(f"Total Double Kills: {total_double_kills}")
print(f"Total Skillshots Hit: {total_skillshots_hit}")
print(f"Total Killing Sprees: {total_killing_sprees}")
print(f"Total Longest Time Spent Living: {total_longest_time_spent_living}")
print("===============================")

# Print the script execution time
print("Script Execution Time:", datetime.now() - start_time)
