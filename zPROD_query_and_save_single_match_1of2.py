#use this in conjunction with PROD_riot_lol_estimate_rank_from_single_match.py to get stats on your latest match.
import os
import json
from dotenv import load_dotenv
from riotwatcher import LolWatcher, ApiError

load_dotenv()

# Load your API key from environment variables or secret storage
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

# Initialize LolWatcher with your API key
lol_watcher = LolWatcher(RIOT_API_KEY)

# Specify the region
region = 'na1'

# Specify the match ID
match_id = 'NA1_4704247243' #set your match

# Use the by_id method to get the match data
try:
    match_data = lol_watcher.match.by_id(region, match_id)
    
    # Save the match_data to a JSON file
    file_name = match_id + '.json'
    with open(file_name, 'w') as file:
        json.dump(match_data, file, indent=4)
    
    print('Match data saved to', file_name)
except ApiError as err:
    if err.response.status_code == 429:
        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        print('This retry-after is handled by default by the RiotWatcher library')
        print('Future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
        print('Match not found.')
    else:
        raise
