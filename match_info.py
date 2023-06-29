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
    try:
        match_details = lol_watcher.match.by_id(my_region, match_id)
        if match_details['info']['queueId'] == 450:
            aram_matches.append(match_details)
    except ApiError as e:
        print(f"Error fetching match {match_id}: {e}")

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
total_game_duration = 0

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

            match_id = match['metadata']['matchId']
            game_duration = match['info']['gameDuration']
            print("===============================")
            print(f"Match ID: \033[34m{match_id}\033[0m")
            print(f"Game Duration: \033[34m{game_duration // 60} minutes\033[0m")
            print(f"Saved as: \033[34m{file_name}\033[0m")
            print("Specific metrics for \033[32mCardyflower\033[0m:")

            # Display individual metrics for the match
            participants = match['info']['participants']
            for participant in participants:
                participant_puuid = participant['puuid']
                if participant_puuid == me['puuid']:
                    print(f"Win: \033[34m{participant['win']}\033[0m")
                    print(f"Champion: \033[34m{participant['championName']}\033[0m")
                    print(f"Kills: \033[34m{participant['kills']}\033[0m")
                    print(f"Deaths: \033[34m{participant['deaths']}\033[0m")
                    print(f"Assists: \033[34m{participant['assists']}\033[0m")
                    try:
                        kda = (participant['kills'] + participant['assists']) / participant['deaths']
                    except ZeroDivisionError:
                        kda = 0.0
                    print(f"KDA: \033[34m{kda:.2f}\033[0m")
                    print(f"Kills per Minute: \033[34m{participant['kills'] / (game_duration / 60):.2f}\033[0m")
                    print(f"Deaths per Minute: \033[34m{participant['deaths'] / (game_duration / 60):.2f}\033[0m")
                    print(f"Assists per Minute: \033[34m{participant['assists'] / (game_duration / 60):.2f}\033[0m")
                    print(f"Damage Dealt: \033[34m{participant['totalDamageDealt']}\033[0m")
                    print(f"Gold Earned: \033[34m{participant['goldEarned']}\033[0m")
                    print("===============================")

                    # Update combined totals
                    total_wins += int(participant['win'])
                    total_kills += participant['kills']
                    total_deaths += participant['deaths']
                    total_assists += participant['assists']
                    total_damage_dealt += participant['totalDamageDealt']
                    total_gold_earned += participant['goldEarned']
                    total_game_duration += game_duration

    # Calculate averages
    average_kills = total_kills / total_matches
    average_deaths = total_deaths / total_matches
    average_assists = total_assists / total_matches
    average_kpm = total_kills / (total_game_duration / 60)
    average_dpm = total_deaths / (total_game_duration / 60)
    average_apm = total_assists / (total_game_duration / 60)

    # Display combined totals and averages
    print("===============================")
    print("Combined Metrics for \033[32mCardyflower:\033[0m")
    print(f"Total Matches: \033[32m{total_matches}\033[0m")
    print(f"Total Wins: \033[32m{total_wins}\033[0m")
    print(f"Average Kills:\033[32m{average_kills:.2f}\033[0m")
    print(f"Average Deaths: \033[32m{average_deaths:.2f}\033[0m")
    print(f"Average Assists: \033[32m{average_assists:.2f}\033[0m")
    print(f"Average Kills per Minute: \033[32m{average_kpm:.2f}\033[0m")
    print(f"Average Deaths per Minute: \033[32m{average_dpm:.2f}\033[0m")
    print(f"Average Assists per Minute: \033[32m{average_apm:.2f}\033[0m")
    print("===============================")
else:
    print("No ARAM matches found.")
