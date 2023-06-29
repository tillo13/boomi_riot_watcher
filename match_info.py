import json
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
from scipy.stats import percentileofscore
from riotwatcher import LolWatcher

load_dotenv()

debug_mode = False  # Set to True to show calculation details, False to hide them

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        raise RuntimeError(f"The environment variable '{name}' is not set.")

riot_api_key = get_env_variable('RIOT_API_KEY')

lol_watcher = LolWatcher(api_key=riot_api_key)

my_region = 'na1'
summoner_name = 'britney phi'  # Set your summoner name here

me = lol_watcher.summoner.by_name(my_region, summoner_name)

def fetch_aram_matches():
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

    return aram_matches

def calculate_kda_score(participant):
    kda = (participant['kills'] + participant['assists']) / participant['deaths'] if participant['deaths'] > 0 else 0

    if kda > 5:
        return 5 + (kda - 5) * 0.25  # Assign a modest increase for KDA above 5
    elif kda >= 3:
        return 3 + (kda - 3) * 0.1  # Higher increase for KDA between 3 and 5
    elif kda >= 1:
        return kda
    else:
        return kda * 0.5  # Assign a lower score for KDA below 1

def calculate_rank(participant, game_duration, metrics):
    rank = ''

    # calculate KDA score and apply custom logic
    kda_score = calculate_kda_score(participant)
    metrics[0] = kda_score  # Replace the first element of metrics (which is KDA Score) with the new KDA score.

    # Define weights for each metric
    weights = [4, 1, -1, 1, 1, 1, 2, 2, -1, 1, 2, -1]

    # Calculate weighted rank score
    rank_score = sum(m * w for m, w in zip(metrics, weights))
    metrics.append(rank_score)


    # Define rank score ranges
    rank_score_ranges = {
        'S+': (percentileofscore(metrics, 18), float('inf')),
        'S': (percentileofscore(metrics, 15), percentileofscore(metrics, 18)),
        'S-': (percentileofscore(metrics, 13), percentileofscore(metrics, 15)),
        'A+': (percentileofscore(metrics, 11), percentileofscore(metrics, 13)),
        'A': (percentileofscore(metrics, 9), percentileofscore(metrics, 11)),
        'A-': (percentileofscore(metrics, 7), percentileofscore(metrics, 9)),
        'B+': (percentileofscore(metrics, 5), percentileofscore(metrics, 7)),
        'B': (percentileofscore(metrics, 3), percentileofscore(metrics, 5)),
        'B-': (percentileofscore(metrics, 1), percentileofscore(metrics, 3)),
        'C+': (0, percentileofscore(metrics, 1)),
        'C': (-percentileofscore(metrics, 1), 0),
        'C-': (-percentileofscore(metrics, 3), -percentileofscore(metrics, 1)),
        'D+': (-percentileofscore(metrics, 5), -percentileofscore(metrics, 3)),
        'D': (-percentileofscore(metrics, 7), -percentileofscore(metrics, 5)),
        'D-': (-float('inf'), -percentileofscore(metrics, 7))
    }

    # Determine the rank
    for rank, score_range in sorted(rank_score_ranges.items(), key=lambda x: x[1][0], reverse=True):
        lower_bound, upper_bound = score_range
        if lower_bound <= rank_score < upper_bound:
            return rank

    return rank

aram_matches = fetch_aram_matches()

# Create a "matches" folder if it doesn't exist
matches_folder = "matches"
if not os.path.exists(matches_folder):
    os.makedirs(matches_folder)
else:
    shutil.rmtree(matches_folder)
    os.makedirs(matches_folder)

# Initialize variables for combined totals and averages
total_matches = len(aram_matches)
total_wins = 0
total_kills = 0
total_deaths = 0
total_assists = 0
total_damage_dealt = 0
total_gold_earned = 0
total_game_duration = 0

# Define the names of the metrics
metric_names = [
    "KDA Score",
    "Kills",
    "Death count (negative)",
    "Assists",
    "Damage per Minute",
    "Gold per Minute",
    "Kill Participation",
    "Team Damage Percentage",
    "Damage Taken on Team Percentage (negative)",
    "Kill Participation",
    "Team Damage Percentage",
    "Damage Taken on Team Percentage (negative)"
]

# Save the match details as JSON files in the "matches" folder
if aram_matches:
    # Save all match details as JSON files in the "matches" folder
    file_names = [os.path.join(matches_folder, f"{match['metadata']['matchId']}.json") for match in aram_matches if not os.path.exists(os.path.join(matches_folder, f"{match['metadata']['matchId']}.json"))]

    if file_names:
        match_json_list = [json.loads(json.dumps(match)) for match in aram_matches if not os.path.exists(os.path.join(matches_folder, f"{match['metadata']['matchId']}.json"))]

        for file_name, match_json in zip(file_names, match_json_list):
            with open(file_name, 'w') as file:
                json.dump(match_json, file)

            match_id = match_json['metadata']['matchId']
            game_duration = match_json['info']['gameDuration']
            print("===============================")
            print(f"Match ID: \033[34m{match_id}\033[0m")
            game_creation_timestamp_ms = match_json['info']['gameCreation']
            game_creation_datetime = datetime.fromtimestamp(game_creation_timestamp_ms / 1000)  # Python expects seconds
            print(f"Match start date: \033[34m{game_creation_datetime}\033[0m")
            print(f"Game Duration: \033[34m{game_duration // 60} minutes\033[0m")
            print(f"Saved as: \033[34m{file_name}\033[0m")
            print(f"Summoner name: \033[32m{summoner_name}\033[0m")
            
            # Initialize the calculation details list for each match
            calculation_details = []
            
            # Display individual metrics for the match
            participants = match_json['info']['participants']
            for participant in participants:
                participant_puuid = participant['puuid']
                if participant_puuid == me['puuid']:
                    # Calculate metrics for the participant
                    kda_score = calculate_kda_score(participant)
                    damage_per_min = participant['totalDamageDealt'] / game_duration
                    gold_per_min = participant['goldEarned'] / game_duration
                    kill_participation = participant['challenges']['killParticipation']
                    team_damage_percentage = participant['challenges']['teamDamagePercentage']
                    damage_taken_percentage = participant['challenges']['damageTakenOnTeamPercentage']
                    
                    # Define the metrics list
                    metrics = [
                        kda_score,
                        participant['kills'],
                        -participant['deaths'],
                        participant['assists'],
                        damage_per_min,
                        gold_per_min,
                        kill_participation,
                        team_damage_percentage,
                        -damage_taken_percentage,
                        participant['challenges']['killParticipation'],
                        participant['challenges']['teamDamagePercentage'],
                        -participant['challenges']['damageTakenOnTeamPercentage']
                    ]
                    # Define weights for each metric
                    weights = [4, 1, -1, 1, 1, 1, 2, 2, -1, 1, 2, -1]
                    # Append calculation details for each metric
                    for metric, weight, name in zip(metrics, weights, metric_names):
                        calculation_details.append(f"{name} ({metric} * {weight}): {metric * weight}")
                    
                    # Here we calculate and print the rank
                    rank = calculate_rank(participant, game_duration, metrics)
                    
                    print(f"Estimated Rank: \033[34m{rank}\033[0m")
                    print(f"Total rank score: \033[33m{metrics[-1]}\033[0m")  # Print in yellow
                    #print(f"KDA Score: {kda_score:.2f}")
                    print(f"Win: \033[34m{participant['win']}\033[0m")
                    print(f"Champion: \033[33m{participant['championName']} (\033[0mlvl: \033[33m{participant['champLevel']}\033[0m, \033[0mexp: \033[33m{participant['champExperience']}\033[0m)\033[0m")
                    
                    # Calculate kills, deaths, and assists per minute
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
                    print(f"Damage per min: {damage_per_min:.2f}")
                    print(f"Kill participation: \033[34m{participant['challenges']['killParticipation'] * 100:.2f}%\033[0m")
                    print(f"Team Damage Perc: \033[34m{participant['challenges']['teamDamagePercentage'] * 100:.2f}%\033[0m")
                    print(f"Damage Taken On Team Perc: \033[34m{participant['challenges']['damageTakenOnTeamPercentage'] * 100:.2f}%\033[0m")
                    
                    # Increment the combined totals and averages
                    total_wins += int(participant['win'])
                    total_kills += participant['kills']
                    total_deaths += participant['deaths']
                    total_assists += participant['assists']
                    total_damage_dealt += participant['totalDamageDealt']
                    total_gold_earned += participant['goldEarned']
                    total_game_duration += game_duration

            # Display the calculation details for the match
            if debug_mode:
                print("- - - -calculations details start- - - -")
                for detail in calculation_details:
                    print(detail)
                print(f"KDA Score: {kda_score:.2f}")
                print("- - - -calculations details end- - - -")
            



            
    else:
        print("No new ARAM matches found.")
else:
    print("No ARAM matches found.")

# Calculate the averages
average_wins = total_wins / total_matches * 100 if total_matches > 0 else 0
average_kills = total_kills / total_matches
average_deaths = total_deaths / total_matches
average_assists = total_assists / total_matches
average_damage_dealt = total_damage_dealt / total_matches
average_gold_earned = total_gold_earned / total_matches
average_game_duration = total_game_duration / total_matches


# Display the combined totals and averages
print("===============================")
print(f"Combined Totals for: \033[32m{summoner_name}\033[0m")
print(f"Total matches: \033[34m{total_matches}\033[0m")
print(f"Total wins: \033[34m{total_wins}\033[0m (\033[34m{average_wins:.2f}%\033[0m)")
print(f"Total kills: \033[34m{total_kills}\033[0m")
print(f"Total deaths: \033[34m{total_deaths}\033[0m")
print(f"Total assists: \033[34m{total_assists}\033[0m")
print(f"Total damage dealt: \033[34m{total_damage_dealt}\033[0m")
print(f"Total gold earned: \033[34m{total_gold_earned}\033[0m")
print(f"Total game duration: \033[34m{total_game_duration // 60}\033[0m minutes")
print(f"Combined Averages for: \033[32m{summoner_name}\033[0m")
print(f"Average kills: \033[34m{average_kills:.2f}\033[0m")
print(f"Average deaths: \033[34m{average_deaths:.2f}\033[0m")
print(f"Average assists: \033[34m{average_assists:.2f}\033[0m")
print(f"Average damage dealt: \033[34m{average_damage_dealt:.2f}\033[0m")
print(f"Average gold earned: \033[34m{average_gold_earned:.2f}\033[0m")
print(f"Average game duration: \033[34m{average_game_duration // 60}\033[0m minutes")
print("===============================")


