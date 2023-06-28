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

# Initialize variables for combined totals and averages
total_matches = len(aram_matches)
total_wins = 0
total_kills = 0
total_deaths = 0
total_assists = 0
total_damage_dealt = 0
total_gold_earned = 0
total_vision_score = 0
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
                    print(f"Damage Dealt: {participant['totalDamageDealt']}")
                    print(f"Gold Earned: {participant['goldEarned']}")
                    print(f"Vision Score: {participant['visionScore']}")
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
                    total_vision_score += participant['visionScore']
                    total_object
