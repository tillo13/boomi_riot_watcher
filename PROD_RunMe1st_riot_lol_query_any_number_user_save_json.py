#2023july3 add your API key to your .env file and kick this off to save all your files for ~2 years to your local drive.
# This script retrieves match details for summoner names provided in the environment variable 'PLAYERS'. 
# It uses the Riot API to fetch ARAM matches and saves them as JSON files in a local directory. 
# The script also keeps track of the number of new and existing matches and provides a summary of the execution.

import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError
import pytz
import numpy as np

start_time = time.time()  # Start the timer

######set these values if you'd like#####
max_matches_to_pull = 1000   # Set the desired number of matches to fetch
my_region = 'na1'  # Set your region

load_dotenv()
riot_api_key = os.getenv('RIOT_API_KEY')
request_timestamps = []

if not riot_api_key:
    raise RuntimeError("The environment variable 'RIOT_API_KEY' is not set.")

lol_watcher = LolWatcher(api_key=riot_api_key)

# Get the summoner names from the environment variable
players_str = os.getenv('PLAYERS')
players = players_str.split(',') if players_str is not None else []

num_users = len(players)  # Count the number of users
total_matches = 0
new_matches = 0
existing_matches = 0

oldest_match_id = None
newest_match_id = None
oldest_game_creation = None
newest_game_creation = None

# ANSI escape codes for color formatting
BLUE = '\033[94m'
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'

print(f"Number of users to process: {num_users}")

for i, summoner_name in enumerate(players):
    summoner_name = summoner_name.strip()  # Remove leading/trailing spaces

    try:
        me = lol_watcher.summoner.by_name(my_region, summoner_name)
        request_timestamps.append(time.time())  # record timestamp of request
        
        # Check the latest logged match for the user
        user_folder = me["name"].replace(" ", "_").lower()  # Convert name to lowercase
        matches_folder = os.path.join("matches", user_folder)  # Creates user-specific path in the matches folder
        latest_match_file = None
        
        if os.path.exists(matches_folder):
            match_files = os.listdir(matches_folder)
            if match_files:
                match_files = [file for file in match_files if file.endswith('.json')]  # Only consider JSON files
                if match_files:
                    match_files.sort(reverse=True)
                    latest_match_file = match_files[0]
        
        latest_game_creation = None
        
        if latest_match_file:
            latest_match_path = os.path.join(matches_folder, latest_match_file)
            if os.path.isfile(latest_match_path):
                try:
                    with open(latest_match_path, 'r') as file:
                        latest_match_details = json.load(file)
                    latest_game_creation = latest_match_details['info']['gameCreation']
                except (json.JSONDecodeError, KeyError):
                    print(f"[{datetime.now()}] Error reading match details from file: {latest_match_path}. Skipping...")
        
        if latest_game_creation:
            latest_game_creation_formatted = datetime.fromtimestamp(latest_game_creation / 1000, pytz.timezone('America/Los_Angeles')).strftime('%Y-%B-%d_%H%M%S')
            print("=============+==============")
            print(f"[{datetime.now()}] {BLUE}{summoner_name}{ENDC}: [{GREEN}Valid user!{ENDC}] Last logged match: {latest_game_creation_formatted}! ({i+1}/{num_users})")
        else:
            print(f"[{datetime.now()}] {BLUE}{summoner_name}{ENDC}: [{GREEN}Valid user!{ENDC}] No previous logged matches found.  Processing! ({i+1}/{num_users})")

        def fetch_aram_matches(max_matches):
            aram_matches = []
            start = 0
            count = 100  # Maximum allowed value

            while len(aram_matches) < max_matches:
                try:
                    my_matches = lol_watcher.match.matchlist_by_puuid(my_region, me['puuid'], start=start, count=count)
                    request_timestamps.append(time.time())  # record timestamp of request
                except ApiError as e:
                    print(f"[{datetime.now()}] Error fetching matchlist: {e}")
                    break  # Exit the loop if an error occurs

                if not my_matches:
                    break  # Exit the loop if the list is empty

                # Fetch match details and check if it's an ARAM match (queueId == 450)
                for match_id in my_matches:
                    try:
                        match_details = lol_watcher.match.by_id(my_region, match_id)
                        request_timestamps.append(time.time())  # record timestamp of request
                        if match_details['info']['queueId'] == 450:
                            aram_matches.append(match_details)
                    except ApiError as e:
                        print(f"[{datetime.now()}] Error fetching match {match_id}: {e}")

                    if len(aram_matches) >= max_matches:
                        break

                start += count  # Increase the start index for the next iteration

            return aram_matches

        aram_matches = fetch_aram_matches(max_matches_to_pull)

        # Create a "matches" folder if it doesn't exist and a user folder
        user_folder = me["name"].replace(" ", "_").lower()  # Convert name to lowercase
        matches_folder = os.path.join("matches", user_folder)  # Creates user-specific path in the matches folder
        if os.path.exists(matches_folder):
            for match in aram_matches:
                match_id = match['metadata']['matchId']
                file_path = os.path.join(matches_folder, f"{match_id}.json")

                if not os.path.exists(file_path):
                    with open(file_path, 'w') as file:
                        json.dump(match, file)
                    print(f"[{datetime.now()}] Saved new match details for Match ID: {match_id}")
                    new_matches += 1
                else:
                    print(f"[{datetime.now()}] Match details for Match ID: {match_id} already exist, skipping.")
                    existing_matches += 1
        else:
            os.makedirs(matches_folder)
            for match in aram_matches:
                match_id = match['metadata']['matchId']
                file_path = os.path.join(matches_folder, f"{match_id}.json")

                with open(file_path, 'w') as file:
                    json.dump(match, file)
                print(f"[{datetime.now()}] Saved new match details for Match ID: {match_id}")
                new_matches += 1

        if aram_matches:
            match_ids = [match['metadata']['matchId'] for match in aram_matches]
            match_creations = [match['info']['gameCreation'] for match in aram_matches]
            oldest_match_id = min(match_ids)
            newest_match_id = max(match_ids)
            oldest_game_creation = min(match_creations)
            newest_game_creation = max(match_creations)

        if not aram_matches:
            print(f"[{datetime.now()}] No ARAM matches found for {summoner_name}.")

        total_matches += len(aram_matches)

    except ApiError as err:
        if err.response.status_code == 404:
            print(f"[{datetime.now()}] {BLUE}{summoner_name}{ENDC}: [{RED}Invalid user!{ENDC}] ({i+1}/{num_users})")
        else:
            raise

elapsed_time = time.time() - start_time  # Calculate elapsed time
oldest_game_creation_formatted = datetime.fromtimestamp(oldest_game_creation / 1000, pytz.timezone('America/Los_Angeles')).strftime('%Y-%B-%d_%H%M%S')
newest_game_creation_formatted = datetime.fromtimestamp(newest_game_creation / 1000, pytz.timezone('America/Los_Angeles')).strftime('%Y-%B-%d_%H%M%S')

print(f"\nSummary:")
print(f"{total_matches} total matches queried.")
print(f"{new_matches} new matches found.")
print(f"{existing_matches} matches already present.")
print(f"Oldest matchID queried: {oldest_match_id} / Game Creation: {oldest_game_creation_formatted}")
print(f"Newest matchID queried: {newest_match_id} / Game Creation: {newest_game_creation_formatted}")
print(f"Total number of queries to Riot API: {len(request_timestamps)}")

# Calculate and print queries per 10 seconds
sorted_requests_timestamps = np.sort(request_timestamps)
queries_in_10_seconds = []
for i in range(len(sorted_requests_timestamps)):
    queries_in_this_interval = np.sum(
        (sorted_requests_timestamps >= sorted_requests_timestamps[i]) &
        (sorted_requests_timestamps < sorted_requests_timestamps[i] + 10))
    queries_in_10_seconds.append(queries_in_this_interval)

print(f"Maximum queries in any 10 seconds interval: {max(queries_in_10_seconds)}")
print(f"Script run time: {elapsed_time} seconds.")
