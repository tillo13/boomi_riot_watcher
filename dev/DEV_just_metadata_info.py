import os
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError

load_dotenv()

# Specify the match ID
match_id = 'NA1_4702476487'

# Deduce the region from the matchID above
region = match_id.split('_')[0]

# Load your API key from environment variables or secret storage
RIOT_API_KEY = os.getenv('RIOT_API_KEY')
OUR_SQUAD = os.getenv('OUR_SQUAD')

# Initialize LolWatcher with your API key
lol_watcher = LolWatcher(RIOT_API_KEY)

def print_field_with_breadcrumbs(field_name, field_value, breadcrumbs="info", color="\033[92m"):
    print(f"{color}{breadcrumbs}->{field_name}: {field_value}\033[0m")

try:
    # Get the match details using LolWatcher's API
    match_info = lol_watcher.match.by_id(region, match_id)

    # Extract specific fields from the "info" section
    game_creation = match_info['info']['gameCreation']
    game_duration = match_info['info']['gameDuration']
    game_end_timestamp = match_info['info']['gameEndTimestamp']
    game_id = match_info['info']['gameId']
    game_mode = match_info['info']['gameMode']
    game_name = match_info['info']['gameName']
    game_start_timestamp = match_info['info']['gameStartTimestamp']
    game_type = match_info['info']['gameType']
    game_version = match_info['info']['gameVersion']
    map_id = match_info['info']['mapId']
    platform_id = match_info['info']['platformId']
    queue_id = match_info['info']['queueId']
    tournament_code = match_info['info']['tournamentCode']
    teams = match_info['info']['teams']

    # Display the extracted fields with breadcrumbs in the terminal
    print("root_info->")
    print_field_with_breadcrumbs("gameCreation", game_creation)
    print_field_with_breadcrumbs("gameDuration", game_duration)
    print_field_with_breadcrumbs("gameEndTimestamp", game_end_timestamp)
    print_field_with_breadcrumbs("gameId", game_id)
    print_field_with_breadcrumbs("gameMode", game_mode)
    print_field_with_breadcrumbs("gameName", game_name)
    print_field_with_breadcrumbs("gameStartTimestamp", game_start_timestamp)
    print_field_with_breadcrumbs("gameType", game_type)
    print_field_with_breadcrumbs("gameVersion", game_version)
    print_field_with_breadcrumbs("mapId", map_id)
    print_field_with_breadcrumbs("platformId", platform_id)
    print_field_with_breadcrumbs("queueId", queue_id)
    print_field_with_breadcrumbs("tournamentCode", tournament_code)

    # Display the teams data in red
    print("")
    print_field_with_breadcrumbs("teams", "", color="\033[91m")
    for i, team in enumerate(teams):
        print_field_with_breadcrumbs(f"Team {i+1}", "", breadcrumbs="teams", color="\033[91m")
        for field_name, field_value in team.items():
            if field_name == "objectives":
                print_field_with_breadcrumbs(field_name, "", breadcrumbs=f"teams->Team {i+1}", color="\033[91m")
                for objective_name, objective_value in field_value.items():
                    for sub_field_name, sub_field_value in objective_value.items():
                        print_field_with_breadcrumbs(sub_field_name, sub_field_value, breadcrumbs=f"teams->Team {i+1}->{field_name}->{objective_name}", color="\033[91m")
            else:
                print_field_with_breadcrumbs(field_name, field_value, breadcrumbs=f"teams->Team {i+1}", color="\033[91m")

    # Display the metadata fields in yellow
    print("")
    metadata = match_info['metadata']
    print_field_with_breadcrumbs("metadata", "", color="\033[93m")
    for field_name, field_value in metadata.items():
        print_field_with_breadcrumbs(field_name, field_value, breadcrumbs="metadata", color="\033[93m")

except ApiError as e:
    print(f"Failed to retrieve match information: {e}")
