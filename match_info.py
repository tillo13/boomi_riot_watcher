import os
import json
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv
from datetime import datetime
from scipy.stats import percentileofscore

load_dotenv()

lol_watcher = LolWatcher(os.getenv('RIOT_API_KEY'))

my_region = 'na1'

summonerName = 'cardyflower'  # Set your summoner name here

me = lol_watcher.summoner.by_name(my_region, summonerName)

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

def calculate_rank(participant, game_duration):
    rank = ''

    # Calculate metrics
    kda = (participant['kills'] + participant['assists']) / participant['deaths'] if participant['deaths'] > 0 else 0
    damage_per_min = participant['totalDamageDealt'] / game_duration
    gold_per_min = participant['goldEarned'] / game_duration
    kill_participation = participant['challenges']['killParticipation']
    team_damage_percentage = participant['challenges']['teamDamagePercentage']
    damage_taken_percentage = participant['challenges']['damageTakenOnTeamPercentage']

    metrics = [
        kda,
        participant['kills'],
        -participant['deaths'],
        participant['assists'],
        damage_per_min,
        gold_per_min,
        kill_participation,
        team_damage_percentage,
        -damage_taken_percentage
    ]
    weights = [3, 1, -1, 1, 1, 1, 2, 2, -1]

    # Calculate weighted rank score
    rank_score = sum(m * w for m, w in zip(metrics, weights))

    # Define rank score ranges based on estimated scores
    rank_score_ranges = {
        'S+': (percentileofscore(metrics, 15), float('inf')),
        'S': (percentileofscore(metrics, 13), percentileofscore(metrics, 15)),
        'S-': (percentileofscore(metrics, 11), percentileofscore(metrics, 13)),
        'A+': (percentileofscore(metrics, 9), percentileofscore(metrics, 11)),
        'A': (percentileofscore(metrics, 7), percentileofscore(metrics, 9)),
        'A-': (percentileofscore(metrics, 5), percentileofscore(metrics, 7)),
        'B+': (percentileofscore(metrics, 3), percentileofscore(metrics, 5)),
        'B': (percentileofscore(metrics, 1), percentileofscore(metrics, 3)),
        'B-': (0, percentileofscore(metrics, 1)),
        'C+': (-percentileofscore(metrics, 1), 0),
        'C': (-percentileofscore(metrics, 3), -percentileofscore(metrics, 1)),
        'C-': (-percentileofscore(metrics, 5), -percentileofscore(metrics, 3)),
        'D+': (-percentileofscore(metrics, 7), -percentileofscore(metrics, 5)),
        'D': (-percentileofscore(metrics, 9), -percentileofscore(metrics, 7)),
        'D-': (-percentileofscore(metrics, 11), -percentileofscore(metrics, 9))
    }

    # Determine the rank
    for rank, score_range in sorted(rank_score_ranges.items(), key=lambda x: x[1][0], reverse=True):
        lower_bound, upper_bound = score_range
        if lower_bound <= rank_score < upper_bound:
            return rank



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
            game_creation_timestamp_ms = match['info']['gameCreation']
            game_creation_datetime = datetime.fromtimestamp(game_creation_timestamp_ms / 1000)  # Python expects seconds
            print(f"Match start date: \033[34m{game_creation_datetime}\033[0m")
            print(f"Game Duration: \033[34m{game_duration // 60} minutes\033[0m")
            print(f"Saved as: \033[34m{file_name}\033[0m")
            print(f"Specific metrics for \033[32m{summonerName}\033[0m:") 

            # Display individual metrics for the match
            participants = match['info']['participants']
            for participant in participants:
                participant_puuid = participant['puuid']
                if participant_puuid == me['puuid']:

                    # Here we calculate and print the rank
                    rank = calculate_rank(participant, game_duration)
                    print(f"Estimated Rank: \033[34m{rank}\033[0m")
                    print(f"Win: \033[34m{participant['win']}\033[0m")
                    print(f"Champion: \033[34m{participant['championName']}\033[0m")

                    # calculate kills, deaths, and assists per minute
                    kpm = participant['kills'] / (game_duration / 60)
                    dpm = participant['deaths'] / (game_duration / 60)
                    apm = participant['assists'] / (game_duration / 60)

                    print(f"Kills: \033[34m{participant['kills']}\033[0m (per min: {kpm:.2f})")
                    print(f"Deaths: \033[34m{participant['deaths']}\033[0m (per min: {dpm:.2f})")
                    print(f"Assists: \033[34m{participant['assists']}\033[0m (per min: {apm:.2f})")

                    try:
                        kda = (participant['kills'] + participant['assists']) / participant['deaths']
                    except ZeroDivisionError:
                        kda = 0.0
                    print(f"KDA: \033[34m{kda:.2f}\033[0m")
                    print(f"Damage Dealt: \033[34m{participant['totalDamageDealt']}\033[0m")
                    print(f"Gold Earned: \033[34m{participant['goldEarned']}\033[0m")
                    print(f"Damage per min: \033[34m{participant['challenges']['damagePerMinute']*1:.2f}\033[0m")
                    print(f"Kill participation: \033[34m{participant['challenges']['killParticipation']*100:.2f}%\033[0m")
                    print(f"Team Damage Perc: \033[34m{participant['challenges']['teamDamagePercentage']*100:.2f}%\033[0m")
                    print(f"Damage Taken On Team Perc: \033[34m{participant['challenges']['damageTakenOnTeamPercentage']*100:.2f}%\033[0m")
                   
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
    print("Combined Metrics for \033[32m{}:\033[0m".format(summonerName))
    print(f"Total Matches: \033[32m{total_matches}\033[0m")
    print(f"Total Wins: \033[32m{total_wins}\033[0m")

    # Calculate overall per-minute averages
    avg_kpm_total = total_kills / (total_game_duration / 60)
    avg_dpm_total = total_deaths / (total_game_duration / 60)
    avg_apm_total = total_assists / (total_game_duration / 60)

    print(f"Kills: \033[32m{total_kills}\033[0m (per min: {avg_kpm_total:.2f})")
    print(f"Deaths: \033[32m{total_deaths}\033[0m (per min: {avg_dpm_total:.2f})")
    print(f"Assists: \033[32m{total_assists}\033[0m (per min: {avg_apm_total:.2f})")
    print("===============================")
else:
    print("No ARAM matches found.")
