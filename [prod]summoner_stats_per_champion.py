import os
import json
from tabulate import tabulate
from datetime import datetime, timezone, timedelta
from termcolor import colored

matches_folder = "matches"  # Specify the folder path

# Get all subdirectories within the matches folder
subdirectories = next(os.walk(matches_folder))[1]

# Initialize variables for combined stats
headers = ["Summoner", "Champ", "Match Count", "Avg KDA", "Kills", "Deaths", "Assists",
           "DoubleKs", "TripleKs", "QuadraKs", "PentaKs", "Max kSpree", "Avg dmg Dealt",
           "Max Kills", "Last Match Played As"]  # Change position of "Avg dmg Dealt"

summoner_data = []

# Color thresholds for each column: (lower_threshold, upper_threshold)
# Values below the lower_threshold will be colored blue, between lower_threshold and upper_threshold (inclusive) will be colored yellow, and above the upper_threshold will be colored green.
color_thresholds = {
    "Matches Played": (5, 20),
    "Avg KDA": (1, 4),
    "Avg Damage Dealt": (18000, 21000),
    "DoubleKs": (1, 8),
    "TripleKs": (1, 5),
    "QuadraKs": (1, 5),
    "PentaKs": (1, 6),
    "Max Killing Spree": (1, 10),
    "Max Kills": (1, 20)  
}


seattle_timezone = timezone(timedelta(hours=-7))  # Define Seattle timezone as UTC-7


# Iterate over the subdirectories and extract the summoner names
for directory in subdirectories:
    summoner_name = directory.replace("_", " ").title()
    summoner_directory = os.path.join(matches_folder, directory)

    # Initialize variables for summoner stats
    summoner_stats = {}

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
                            for participant in participants:
                                if "summonerName" in participant and participant["summonerName"].lower().replace(" ",
                                                                                                                 "") == summoner_name.lower().replace(
                                        " ", ""):
                                    champion_name = participant["championName"]
                                    if champion_name == "MonkeyKing":
                                        champion_name = "Wukong"
                                    if champion_name not in summoner_stats:
                                        # Initialize stats for the champion
                                        summoner_stats[champion_name] = {
                                            "game_count": 0,
                                            "total_kda": 0,
                                            "total_damage_dealt": 0,
                                            "total_double_kills": 0,
                                            "total_triple_kills": 0,
                                            "total_quadra_kills": 0,
                                            "total_penta_kills": 0,
                                            "total_killing_sprees": 0,
                                            "total_kills": 0,
                                            "total_deaths": 0,
                                            "total_assists": 0,
                                            "max_kills": 0,  # Add max_kills
                                            "last_match_timestamp": None
                                        }
                                    stats = summoner_stats[champion_name]
                                    if "challenges" in participant and "kda" in participant["challenges"]:
                                        stats["total_kda"] += participant["challenges"]["kda"]
                                    if "challenges" in participant and "killingSprees" in participant["challenges"]:
                                        stats["total_killing_sprees"] += participant["challenges"]["killingSprees"]
                                    if "champExperience" in participant:
                                        stats["total_damage_dealt"] += participant["champExperience"]
                                    if "kills" in participant:
                                        stats["total_kills"] += participant["kills"]  # Add total kills
                                        if participant["kills"] == 2:
                                            stats["total_double_kills"] += 1
                                        elif participant["kills"] == 3:
                                            stats["total_triple_kills"] += 1
                                        elif participant["kills"] == 4:
                                            stats["total_quadra_kills"] += 1
                                        elif participant["kills"] == 5:
                                            stats["total_penta_kills"] += 1
                                        # Update max_kills
                                        if participant["kills"] > stats["max_kills"]:
                                            stats["max_kills"] = participant["kills"]
                                    if "deaths" in participant:
                                        stats["total_deaths"] += participant["deaths"]  # Add total deaths
                                    if "assists" in participant:
                                        stats["total_assists"] += participant["assists"]  # Add total assists
                                    stats["game_count"] += 1
                                    # Update the last match timestamp
                                    if "gameCreation" in json_data["info"]:
                                        game_creation_timestamp = json_data["info"]["gameCreation"] / 1000  # Convert to seconds
                                        game_creation_datetime = datetime.fromtimestamp(game_creation_timestamp,
                                                                                        timezone.utc)
                                        if stats["last_match_timestamp"] is None or game_creation_datetime > stats[
                                            "last_match_timestamp"]:
                                            stats["last_match_timestamp"] = game_creation_datetime

                    except json.JSONDecodeError:
                        continue

    # Process summoner stats for each champion
    for champion_name, stats in summoner_stats.items():
        game_count = stats["game_count"]
        total_kda = stats["total_kda"]
        total_damage_dealt = stats["total_damage_dealt"]
        total_double_kills = stats["total_double_kills"]
        total_triple_kills = stats["total_triple_kills"]
        total_quadra_kills = stats["total_quadra_kills"]
        total_penta_kills = stats["total_penta_kills"]
        total_killing_sprees = stats["total_killing_sprees"]
        total_kills = stats["total_kills"]
        total_deaths = stats["total_deaths"]
        total_assists = stats["total_assists"]
        max_kills = stats["max_kills"]  # Retrieve max_kills
        last_match_timestamp = stats["last_match_timestamp"]

        average_kda = total_kda / game_count if game_count > 0 else 0
        average_damage_dealt = total_damage_dealt / game_count if game_count > 0 else 0

        summoner_data.append(
            (summoner_name, champion_name, game_count, average_kda, average_damage_dealt,
             total_kills, total_deaths, total_assists, total_double_kills,
             total_triple_kills, total_quadra_kills, total_penta_kills,
             total_killing_sprees, max_kills, last_match_timestamp)  # Add max_kills
        )

# Sort summoner data by game count in descending order
summoner_data.sort(key=lambda x: int(''.join(filter(str.isdigit, str(x[2])))), reverse=True)

# Process summoner data and add the "last match played timestamp"
# Process summoner data and add the "last match played timestamp"
for i, summoner in enumerate(summoner_data):
    summoner_name, champion_name, game_count, average_kda, average_damage_dealt, \
    total_kills, total_deaths, total_assists, total_double_kills, total_triple_kills, \
    total_quadra_kills, total_penta_kills, total_killing_sprees, max_kills, last_match_timestamp = summoner  # Add max_kills

    # Convert timestamp to the desired format
    if last_match_timestamp is not None:
        last_match_timestamp = last_match_timestamp.astimezone(seattle_timezone).strftime("%Y-%B-%d_%H%M%S")

    # Add color to each column based on its value, excluding summoner name, champion name, and last match played columns
    colored_game_count = colored(game_count, "blue" if game_count < color_thresholds["Matches Played"][0] else "yellow" if color_thresholds["Matches Played"][0] <= game_count <= color_thresholds["Matches Played"][1] else "green")
    colored_average_kda = colored("{:.3f}".format(average_kda), "blue" if average_kda < color_thresholds["Avg KDA"][0] else "yellow" if color_thresholds["Avg KDA"][0] <= average_kda <= color_thresholds["Avg KDA"][1] else "green")
    colored_average_damage_dealt = colored("{:.0f}".format(average_damage_dealt), "blue" if average_damage_dealt < color_thresholds["Avg Damage Dealt"][0] else "yellow" if color_thresholds["Avg Damage Dealt"][0] <= average_damage_dealt <= color_thresholds["Avg Damage Dealt"][1] else "green")
    #no color cells
    colored_total_kills = str(total_kills)
    colored_total_deaths = str(total_deaths)
    colored_total_assists = str(total_assists)   
    #no color cells
    colored_total_double_kills = colored(total_double_kills, "blue" if total_double_kills < color_thresholds["DoubleKs"][0] else "yellow" if color_thresholds["DoubleKs"][0] <= total_double_kills <= color_thresholds["DoubleKs"][1] else "green")
    colored_total_triple_kills = colored(total_triple_kills, "blue" if total_triple_kills < color_thresholds["TripleKs"][0] else "yellow" if color_thresholds["TripleKs"][0] <= total_triple_kills <= color_thresholds["TripleKs"][1] else "green")
    colored_total_quadra_kills = colored(total_quadra_kills, "blue" if total_quadra_kills < color_thresholds["QuadraKs"][0] else "yellow" if color_thresholds["QuadraKs"][0] <= total_quadra_kills <= color_thresholds["QuadraKs"][1] else "green")
    colored_total_penta_kills = colored(total_penta_kills, "blue" if total_penta_kills < color_thresholds["PentaKs"][0] else "yellow" if color_thresholds["PentaKs"][0] <= total_penta_kills <= color_thresholds["PentaKs"][1] else "green")
    colored_total_killing_sprees = colored(total_killing_sprees, "blue" if total_killing_sprees < color_thresholds["Max Killing Spree"][0] else "yellow" if color_thresholds["Max Killing Spree"][0] <= total_killing_sprees <= color_thresholds["Max Killing Spree"][1] else "green")
    colored_max_kills = colored(max_kills, "blue" if max_kills < color_thresholds["Max Kills"][0] else "yellow" if color_thresholds["Max Kills"][0] <= max_kills <= color_thresholds["Max Kills"][1] else "green")  # Add color for max_kills

    summoner_data[i] = (summoner_name, champion_name, colored_game_count, colored_average_kda,
                        colored_total_kills, colored_total_deaths, colored_total_assists,
                        colored_total_double_kills, colored_total_triple_kills,
                        colored_total_quadra_kills, colored_total_penta_kills,
                        colored_total_killing_sprees, colored_average_damage_dealt,  # Move "Avg dmg Dealt"
                        colored_max_kills, last_match_timestamp)  # Add colored_max_kills

# Print the list of summoner names, champion names, and stats in tabular format
print(tabulate(summoner_data, headers=headers))
