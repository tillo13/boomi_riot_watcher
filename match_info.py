import os
import json
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv

load_dotenv()

lol_watcher = LolWatcher(os.getenv('RIOT_API_KEY'))

my_region = 'na1'

me = lol_watcher.summoner.by_name(my_region, 'cardyflower')

my_matches = lol_watcher.match.matchlist_by_puuid(my_region, me['puuid'])

aram_matches = []

# Fetch match details and check if it's an ARAM match (queueId == 450)
for match_id in my_matches:
    match_details = lol_watcher.match.by_id(my_region, match_id)
    if match_details['info']['queueId'] == 450:
        aram_matches.append(match_details)

# Create a "matches" folder if it doesn't exist
matches_folder = "matches"
if not os.path.exists(matches_folder):
    os.makedirs(matches_folder)
else:
    # Delete existing .json files in the "matches" directory
    for file_name in os.listdir(matches_folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(matches_folder, file_name)
            os.remove(file_path)

# Initialize variables for combined totals and averages
total_matches = len(aram_matches)
total_wins = 0
total_kills = 0
total_deaths = 0
total_assists = 0
total_damage_dealt = 0
total_gold_earned = 0
total_objective_control = 0
total_turret_damage = 0
total_survival_time = 0

# Save the match details as JSON files in the "matches" folder
if aram_matches:
    for match in aram_matches:
        file_name = os.path.join(matches_folder, f"{match['metadata']['matchId']}.json")
        if os.path.exists(file_name):
            print(f"Skipping existing match: {file_name}")
        else:
            # Convert the match details to a JSON-compatible format
            match_json = json.loads(json.dumps(match))
            
            with open(file_name, 'w') as file:
                json.dump(match_json, file)
            
            print(f"Saved new match: {file_name}")
            
            # Display individual metrics for the match
            participants = match['info']['participants']
            for participant in participants:
                participant_puuid = participant['puuid']
                if participant_puuid == me['puuid']:
                    print("Metrics for Cardyflower:")
                    print(f"Win: {participant['win']}")
                    print(f"Champion: {participant['championName']}")
                    print(f"Kills: {participant['kills']}")
                    print(f"Deaths: {participant['deaths']}")
                    print(f"Assists: {participant['assists']}")
                    print(f"KDA: {(participant['kills'] + participant['assists']) / participant['deaths']:.2f}")
                    print(f"Damage Dealt: {participant['totalDamageDealt']}")
                    print(f"Gold Earned: {participant['goldEarned']}")
                    print(f"Objective Control: {participant['objectivesStolen']}")
                    print(f"Turret Damage: {participant['damageDealtToTurrets']}")
                    print(f"Survival Time: {participant['totalTimeSpentDead']} seconds")
                    print("===============================")
                    
                    # Update combined totals
                    total_wins += int(participant['win'])
                    total_kills += participant['kills']
                    total_deaths += participant['deaths']
                    total_assists += participant['assists']
                    total_damage_dealt += participant['totalDamageDealt']
                    total_gold_earned += participant['goldEarned']
                    total_objective_control += participant['objectivesStolen']
                    total_turret_damage += participant['damageDealtToTurrets']
                    total_survival_time += participant['totalTimeSpentDead']
                    
    # Calculate averages
    average_kills = total_kills / total_matches
    average_deaths = total_deaths / total_matches
    average_assists = total_assists / total_matches
    average_damage_dealt = total_damage_dealt / total_matches
    average_gold_earned = total_gold_earned / total_matches
    average_objective_control = total_objective_control / total_matches
    average_turret_damage = total_turret_damage / total_matches
    average_survival_time = total_survival_time / total_matches
    
    # Display combined totals and averages
    print("Combined Metrics for Cardyflower:")
    print(f"Total Matches: {total_matches}")
    print(f"Total Wins: {total_wins}")
    print(f"Average Kills: {average_kills}")
    print(f"Average Deaths: {average_deaths}")
    print(f"Average Assists: {average_assists}")
    print(f"Average KDA: {(average_kills + average_assists) / average_deaths:.2f}")
    print(f"Average Damage Dealt: {average_damage_dealt}")
    print(f"Average Gold Earned: {average_gold_earned}")
    print(f"Average Objective Control: {average_objective_control}")
    print(f"Average Turret Damage: {average_turret_damage}")
    print(f"Average Survival Time: {average_survival_time} seconds")
else:
    print("No ARAM matches found.")
