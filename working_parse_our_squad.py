import os
import json
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

# Save the match_data to a JSON file
directory = 'single_match_analysis'

# Create the directory if it doesn't exist
if not os.path.exists(directory):
    os.makedirs(directory)

file_name = match_id + '.json'
file_path = os.path.join(directory, file_name)

# Split the OUR_SQUAD variable into a list of usernames
users = OUR_SQUAD.split(',')

# Process each user in the squad
matching_participants = []

def print_field_with_breadcrumbs(field_name, field_value, breadcrumbs="info", color="\033[92m"):
    # Adjust the color according to the breadcrumbs
    if breadcrumbs.endswith("teams"):
        print(f"{breadcrumbs}->{field_name}: \033[91m{field_value}\033[0m")
    else:
        print(f"{breadcrumbs}->{field_name}: \033[92m{field_value}\033[0m")

def check_user_in_squad(user):
    try:
        match_data = lol_watcher.match.by_id(region, match_id)
        participants = match_data['info']['participants']
        for participant in participants:
            summoner_name = participant['summonerName']
            if summoner_name == user:
                print("---")
                print(f"Looking for \033[94m{user}\033[0m in OUR_SQUAD variable...\nFOUND!\nprocessing script...")
                print("---")
                return True
        print("---")
        print(f"Looking for \033[94m{user}\033[0m in OUR_SQUAD variable...\nNOT FOUND!\nNot processing anything more, Checking next user...")
        print("---")
        return False
    except ApiError as e:
        print(f"Failed to retrieve match information: {e}")
        return False

def process_user(user, matching_participants):
    #print(f"checking {user} in OUR_SQUAD variable...")
    if user in OUR_SQUAD:
        print("FOUND!")
        try:
            # Specify the match ID
            match_id = 'NA1_4702476487'

            # Deduce the region from the matchID above
            region = match_id.split('_')[0]

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
            print("\033[93mteams\033[0m")
            for i, team in enumerate(teams):
                print(f"\033[93mTeam {i+1}\033[0m")
                for field_name, field_value in team.items():
                    if field_name == "objectives":
                        print(f"teams->Team {i+1}->{field_name}")
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

            print("")

            def print_values_with_breadcrumbs(data, breadcrumbs=''):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            if breadcrumbs == "":
                                new_breadcrumbs = key
                            else:
                                new_breadcrumbs = f"{breadcrumbs}->{key}"
                            print_values_with_breadcrumbs(value, new_breadcrumbs)
                        else:
                            print(f"{breadcrumbs}->{key}: \033[94m{value}\033[0m")
                elif isinstance(data, list):
                    for index, value in enumerate(data):
                        if breadcrumbs == "":
                            new_breadcrumbs = f"[{index}]"
                        else:
                            new_breadcrumbs = f"{breadcrumbs}->[{index}]"
                        print_values_with_breadcrumbs(value, new_breadcrumbs)

            match_data = lol_watcher.match.by_id(region, match_id)
            participants = match_data['info']['participants']

            found_match = False

            for participant in participants:
                summoner_name = participant['summonerName']
                participant_id = participant['participantId']
                if summoner_name == user:
                    print("**********")
                    print(f"Parsed stats for the matching participant \033[94m{user}\033[0m:")
                    print("**********")
                    print_values_with_breadcrumbs(participant, f"info->participants->[{participant_id}]")
                    found_match = True
                    matching_participants.append({
                        'summoner_name': user,
                        'participant_id': participant_id
                    })
                    break

            if not found_match:
                print(f"No members of OUR_SQUAD [variable set at the beginning] were found in the match: {match_id}")

        except ApiError as err:
            if err.response.status_code == 429:
                print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
                print('This retry-after is handled by default by the RiotWatcher library')
            elif err.response.status_code == 404:
                print('Match not found.')
            else:
                raise
    else:
        print("NOT FOUND!")
        print("Not processing anything more, Checking next user...")

# Split the OUR_SQUAD variable into a list of usernames
users = OUR_SQUAD.split(',')

# Process each user in the squad
matching_participants = []
    # Rest of your code...

for user in users:
    # Call the check_user_in_squad function for the current user
    if check_user_in_squad(user):
        # If the user is found in the match, then process the user
        process_user(user, matching_participants)

# Check if there are matching participants
if matching_participants:
    # Display the number of squad members in the match and their details
    print(f"\nNumber of OUR_SQUAD members in the match: {len(matching_participants)}")
    for participant in matching_participants:
        print(f"Summoner Name: {participant['summoner_name']}")
        print(f"Participant ID: {participant['participant_id']}")
        print()