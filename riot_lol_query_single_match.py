# This script fetches match data from the Riot Games API using the RiotWatcher library.
# It requires the following dependencies: os, json, dotenv, riotwatcher.
# Make sure to set your Riot API key as the value of the RIOT_API_KEY environment variable.

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
match_id = 'NA1_4679137573' #set your match

# Use the by_id method to get the match data
try:
    match_data = lol_watcher.match.by_id(region, match_id)
    #pick your choice of pretty json or not just block json
    #print(json.dumps(match_data, indent=4))  # Use json.dumps with indent
    print(match_data)
except ApiError as err:
    if err.response.status_code == 429:
        print('We should retry in {} seconds.'.format(err.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
        print('Match not found.')
    else:
        raise
