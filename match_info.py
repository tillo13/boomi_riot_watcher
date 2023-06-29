import json
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv
from scipy.stats import percentileofscore
from riotwatcher import LolWatcher

load_dotenv()

debug_mode = False  # Set to True to show calculation details, False to hide them
KDA_WEIGHT = 10  # Change this value to tweak the value KDA has on the summoners Total Rank score.  
#In the case of KDA_WEIGHT being 1, the total sum of the weights (including `KDA_WEIGHT`) would be 10. Therefore, the KDA Score would contribute 10% (1 out of 10) of the total weight.  Alternatively if KDA_WEIGHT is set to 10, it would contribute over half (10 out of 19, or approximately 52.63%) of the total weight. 

riot_api_key = os.getenv('RIOT_API_KEY')

if not riot_api_key:
    raise RuntimeError("The environment variable 'RIOT_API_KEY' is not set.")

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
def calculate_total_rank_grade(total_rank_score):
    if total_rank_score >= 210:
        return 'S+'
    elif total_rank_score >= 200:
        return 'S'
    elif total_rank_score >= 190:
        return 'S-'
    elif total_rank_score >= 180:
        return 'A+'
    elif total_rank_score >= 170:
        return 'A'
    elif total_rank_score >= 160:
        return 'A-'
    elif total_rank_score >= 150:
        return 'B+'
    elif total_rank_score >= 140:
        return 'B'
    elif total_rank_score >= 130:
        return 'B-'
    elif total_rank_score >= 120:
        return 'C+'
    elif total_rank_score >= 110:
        return 'C'
    elif total_rank_score >= 100:
        return 'C-'
    elif total_rank_score >= 90:
        return 'D+'
    elif total_rank_score >= 80:
        return 'D'
    else:
        return 'D-'

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

def calculate_rank(participant, game_duration, metrics, weights):
    rank = ''
    weights[0] = KDA_WEIGHT
    weights = [KDA_WEIGHT, 1, -1, 1, 1, 1, 2, 2, -1, 1, 2, -1]
    rank_score = sum(m * w for m, w in zip(metrics, weights))
    metrics.append(rank_score)

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
total_penta_kills = 0
total_quadra_kills = 0
total_triple_kills = 0
total_double_kills = 0
total_skillshots_hit = 0
total_killing_sprees = 0
total_longest_time_spent_living = 0

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

                    
                    # Fetch these metrics without adding them to any calculations, yet.
                    penta_kills = participant['pentaKills']
                    quadra_kills = participant['quadraKills']
                    triple_kills = participant['tripleKills']
                    double_kills = participant['doubleKills']
                    skillshots_hit = participant['challenges']['skillshotsHit']
                    killing_sprees = participant['killingSprees']
                    longest_time_spent_living = participant['longestTimeSpentLiving']

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
                    rank = calculate_rank(participant, game_duration, metrics, weights)
                    
                    print(f"Total rank score: \033[33m{metrics[-1]}\033[0m")  # Print in yellow
                    total_rank_grade = calculate_total_rank_grade(metrics[-1])
                    # Display the total grade rank
                    print(f"Total rank grade: \033[34m{total_rank_grade}\033[0m")
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
                    print(f"Penta Kills: \033[34m{penta_kills}\033[0m")
                    print(f"Quadra Kills: \033[34m{quadra_kills}\033[0m")
                    print(f"Triple Kills: \033[34m{triple_kills}\033[0m")
                    print(f"Double Kills: \033[34m{double_kills}\033[0m")
                    print(f"Skillshots Hit: \033[34m{skillshots_hit}\033[0m")
                    print(f"Killing Sprees: \033[34m{killing_sprees}\033[0m")
                    print(f"Longest Time Spent Living: \033[34m{longest_time_spent_living} seconds\033[0m")
                    print(f"Damage Dealt: \033[34m{participant['totalDamageDealt']}\033[0m")
                    print(f"Gold Earned: \033[34m{participant['goldEarned']}\033[0m")
                    print(f"Damage per min: \033[34m{damage_per_min:.2f}\033[0m")
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
                    total_penta_kills += penta_kills
                    total_quadra_kills += quadra_kills
                    total_triple_kills += triple_kills
                    total_double_kills += double_kills
                    total_skillshots_hit += skillshots_hit
                    total_killing_sprees += killing_sprees
                    total_longest_time_spent_living += longest_time_spent_living

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
average_penta_kills = total_penta_kills / total_matches
average_quadra_kills = total_quadra_kills / total_matches
average_triple_kills = total_triple_kills / total_matches
average_double_kills = total_double_kills / total_matches
average_skillshots_hit = total_skillshots_hit / total_matches
average_killing_sprees = total_killing_sprees / total_matches
average_longest_time_spent_living = total_longest_time_spent_living / total_matches

# Display the combined totals and averages
print("===============================")
print(f"Totals/Averages for: \033[32m{summoner_name}\033[0m")
print(f"Total matches in query: \033[34m{total_matches}\033[0m")
print(f"Total wins: \033[34m{total_wins}\033[0m (\033[34m{average_wins:.2f}%\033[0m)")
print(f"Total kills: \033[34m{total_kills}\033[0m | Average Kills: \033[34m{average_kills:.2f}\033[0m")
print(f"Total deaths: \033[34m{total_deaths}\033[0m | Average Deaths: \033[34m{average_deaths:.2f}\033[0m")
print(f"Total assists: \033[34m{total_assists}\033[0m | Average Assists: \033[34m{average_assists:.2f}\033[0m")
print(f"Total Penta Kills: \033[34m{total_penta_kills}\033[0m | Average Penta Kills: \033[34m{average_penta_kills:.2f}\033[0m")
print(f"Total Quadra Kills: \033[34m{total_quadra_kills}\033[0m | Average Quadra Kills: \033[34m{average_quadra_kills:.2f}\033[0m")
print(f"Total Triple Kills: \033[34m{total_triple_kills}\033[0m | Average Triple Kills: \033[34m{average_triple_kills:.2f}\033[0m")
print(f"Total Double Kills: \033[34m{total_double_kills}\033[0m | Average Double Kills: \033[34m{average_double_kills:.2f}\033[0m")
print(f"Total Skillshots Hit: \033[34m{total_skillshots_hit}\033[0m | Average Skillshots Hit: \033[34m{average_skillshots_hit:.2f}\033[0m")
print(f"Total Killing Sprees: \033[34m{total_killing_sprees}\033[0m | Average Killing Sprees: \033[34m{average_killing_sprees:.2f}\033[0m")
print(f"Total Longest Time Spent Living: \033[34m{total_longest_time_spent_living} seconds\033[0m | Average Longest Time Spent Living: \033[34m{average_longest_time_spent_living:.2f} seconds\033[0m")
print(f"Total damage dealt: \033[34m{total_damage_dealt}\033[0m | Average damage dealt: \033[34m{average_damage_dealt:.2f}\033[0m")
print(f"Total gold earned: \033[34m{total_gold_earned}\033[0m | Average gold earned: \033[34m{average_gold_earned:.2f}\033[0m")
print(f"Total game duration: \033[34m{total_game_duration // 60} minutes\033[0m | Average game duration: \033[34m{average_game_duration // 60} minutes\033[0m")
print("===============================")