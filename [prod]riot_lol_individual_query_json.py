import os
import json
from tabulate import tabulate
from datetime import datetime, timezone, timedelta

matches_folder = "matches"  # Specify the folder path

# Get all subdirectories within the matches folder
subdirectories = next(os.walk(matches_folder))[1]

# Initialize variables for combined stats
combined_game_count = 0
combined_total_kda = 0
combined_total_damage_dealt = 0
combined_total_damage_taken = 0
combined_total_healing = 0
combined_total_double_kills = 0
combined_total_triple_kills = 0
combined_total_quadra_kills = 0
combined_total_penta_kills = 0

# Iterate over the subdirectories and extract the summoner names
summoner_data = []
combined_summoners = ["Milltill005", "Lilla Bryar", "Anonobot", "Cardyflower", "Statfame"]

for directory in subdirectories:
    summoner_name = directory.replace("_", " ").title()
    summoner_directory = os.path.join(matches_folder, directory)

    game_count = 0
    total_kda = 0
    total_damage_dealt = 0
    total_damage_taken = 0
    total_healing = 0
    total_double_kills = 0
    total_triple_kills = 0
    total_quadra_kills = 0
    total_penta_kills = 0

    files_skipped = 0
    summoner_puuid = None

    # Traverse the summoner's directory tree and process the JSON files
    for root, dirs, files in os.walk(summoner_directory):
        for file in files:
            if file.endswith(".json"):
                json_file_path = os.path.join(root, file)
                with open(json_file_path, "r") as json_file:
                    try:
                        json_data = json.load(json_file)
                        if "info" in json_data and "participants" in json_data["info"]:
                            participants = json_data["info"]["participants"]
                            summoner_participants = [
                                participant for participant in participants
                                if "summonerName" in participant and
                                participant["summonerName"].lower().replace(" ", "") == summoner_name.lower().replace(" ", "")
                            ]
                            for participant in summoner_participants:
                                if "challenges" in participant and "kda" in participant["challenges"]:
                                    total_kda += participant["challenges"]["kda"]
                                if "puuid" in participant:
                                    summoner_puuid = participant["puuid"]
                                if "champExperience" in participant:
                                    total_damage_dealt += participant["champExperience"]
                                if "physicalDamageTaken" in participant:
                                    total_damage_taken += participant["physicalDamageTaken"]
                                if "totalHeal" in participant:
                                    total_healing += participant["totalHeal"]
                                if "kills" in participant:
                                    if participant["kills"] == 2:
                                        total_double_kills += 1
                                    elif participant["kills"] == 3:
                                        total_triple_kills += 1
                                    elif participant["kills"] == 4:
                                        total_quadra_kills += 1
                                    elif participant["kills"] == 5:
                                        total_penta_kills += 1
                            game_count += 1
                    except json.JSONDecodeError:
                        files_skipped += 1
                        continue
            else:
                files_skipped += 1

    average_kda = total_kda / game_count if game_count > 0 else 0
    average_damage_dealt = total_damage_dealt / game_count if game_count > 0 else 0
    average_damage_taken = total_damage_taken / game_count if game_count > 0 else 0
    average_healing = total_healing / game_count if game_count > 0 else 0

    summoner_data.append((summoner_name, summoner_puuid, game_count, average_kda, average_damage_dealt,
                          average_damage_taken, average_healing, total_double_kills, total_triple_kills,
                          total_quadra_kills, total_penta_kills, files_skipped))

    if summoner_name in combined_summoners:
        # Accumulate stats for combined summoner
        combined_game_count += game_count
        combined_total_kda += total_kda
        combined_total_damage_dealt += total_damage_dealt
        combined_total_damage_taken += total_damage_taken
        combined_total_healing += total_healing
        combined_total_double_kills += total_double_kills
        combined_total_triple_kills += total_triple_kills
        combined_total_quadra_kills += total_quadra_kills
        combined_total_penta_kills += total_penta_kills

# Calculate averages for combined summoner
combined_average_kda = combined_total_kda / combined_game_count if combined_game_count > 0 else 0
combined_average_damage_dealt = combined_total_damage_dealt / combined_game_count if combined_game_count > 0 else 0
combined_average_damage_taken = combined_total_damage_taken / combined_game_count if combined_game_count > 0 else 0
combined_average_healing = combined_total_healing / combined_game_count if combined_game_count > 0 else 0

# Sort summoner data by summoner name
summoner_data.sort(key=lambda x: x[0].lower())

# Convert timestamp to Seattle timezone
seattle_timezone = timezone(timedelta(hours=-7))  # UTC-7 for Seattle

# Process summoner data and add the "last match played timestamp"
for i, summoner in enumerate(summoner_data):
    summoner_name, summoner_puuid, game_count, average_kda, average_damage_dealt, average_damage_taken, average_healing, \
    total_double_kills, total_triple_kills, total_quadra_kills, total_penta_kills, files_skipped = summoner

    last_match_timestamp = None
    latest_game_creation = 0

    # Traverse the summoner's directory tree and find the latest gameCreation timestamp
    for root, dirs, files in os.walk(os.path.join(matches_folder, summoner_name.lower().replace(" ", "_"))):
        for file in files:
            if file.endswith(".json"):
                json_file_path = os.path.join(root, file)
                with open(json_file_path, "r") as json_file:
                    try:
                        json_data = json.load(json_file)
                        if "info" in json_data and "gameCreation" in json_data["info"]:
                            game_creation_timestamp = json_data["info"]["gameCreation"] / 1000  # Convert to seconds
                            game_creation_datetime = datetime.fromtimestamp(game_creation_timestamp, seattle_timezone)
                            if game_creation_timestamp > latest_game_creation:
                                latest_game_creation = game_creation_timestamp
                                last_match_timestamp = game_creation_datetime.strftime("%Y-%B-%d_%H%M%S")
                    except json.JSONDecodeError:
                        continue

    summoner_data[i] += (last_match_timestamp,)

# Print the list of summoner names, PUUIDs, game counts, averages, totals, and last match timestamps with colored output
print("Summoner Data:")
for summoner_name, summoner_puuid, game_count, average_kda, average_damage_dealt, average_damage_taken, average_healing, \
    total_double_kills, total_triple_kills, total_quadra_kills, total_penta_kills, files_skipped, last_match_timestamp in summoner_data:
    print(f"Summoner Name: \033[32m{summoner_name}\033[0m")
    print(f"PUUID: \033[34m{summoner_puuid}\033[0m")
    print(f"Matches Played: \033[34m{game_count}\033[0m")
    print(f"Average KDA: \033[34m{average_kda:.2f}\033[0m")
    print(f"Average Damage Dealt: \033[34m{average_damage_dealt}\033[0m")
    print(f"Average Damage Taken: \033[34m{average_damage_taken}\033[0m")
    print(f"Average Healing: \033[34m{average_healing}\033[0m")
    print(f"Total Double Kills: \033[34m{total_double_kills}\033[0m")
    print(f"Total Triple Kills: \033[34m{total_triple_kills}\033[0m")
    print(f"Total Quadra Kills: \033[34m{total_quadra_kills}\033[0m")
    print(f"Total Penta Kills: \033[34m{total_penta_kills}\033[0m")
    print(f"Files Skipped: \033[33m{files_skipped}\033[0m")
    print(f"Last Match Played: \033[34m{last_match_timestamp}\033[0m")
    print()

# Print combined summoner's stats
print("+++++++++++")
print("Combined Summoner Data:")
print("Summoner Name: \033[32mOne-Combined\033[0m")
print("PUUID: \033[34mmerged\033[0m")
print(f"Matches Played: \033[34m{combined_game_count}\033[0m")
print(f"Average KDA: \033[34m{combined_average_kda:.2f}\033[0m")
print(f"Average Damage Dealt: \033[34m{combined_average_damage_dealt}\033[0m")
print(f"Average Damage Taken: \033[34m{combined_average_damage_taken}\033[0m")
print(f"Average Healing: \033[34m{combined_average_healing}\033[0m")
print(f"Total Double Kills: \033[34m{combined_total_double_kills}\033[0m")
print(f"Total Triple Kills: \033[34m{combined_total_triple_kills}\033[0m")
print(f"Total Quadra Kills: \033[34m{combined_total_quadra_kills}\033[0m")
print(f"Total Penta Kills: \033[34m{combined_total_penta_kills}\033[0m")

# Create a list of headers for the table.
headers = ["Summoner Name", "Matches Played", "Avg KDA", "Avg Damage Dealt",
           "Avg Damage Taken", "DoubleKs", "TripleKs", "QuadraKs", "PentaKs", "Last Match Played"]

# Collect the summoner data without the PUUID, Files Skipped, and Average Healing
summoner_data_no_puuid = [(name, game_count, avg_kda, avg_damage_dealt, avg_damage_taken,
                           dbl_kills, triple_kills, quadra_kills, penta_kills, last_match)
                          for name, _, game_count, avg_kda, avg_damage_dealt, avg_damage_taken,
                          _, dbl_kills, triple_kills, quadra_kills, penta_kills, _, last_match in summoner_data]

# Collect the combined summoner data without the PUUID and Average Healing
combined_data_no_puuid = [("One-Combined", combined_game_count, combined_average_kda,
                           combined_average_damage_dealt, combined_average_damage_taken,
                           combined_total_double_kills, combined_total_triple_kills,
                           combined_total_quadra_kills, combined_total_penta_kills, "")]

# Append the combined data to the summoner data
summoner_data_no_puuid.append(combined_data_no_puuid[0])

# Print the data in a table
print("Summoner Data:")
print(tabulate(summoner_data_no_puuid, headers=headers))
