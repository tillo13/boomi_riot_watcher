# This script retrieves summoner data for a specific user from the Riot Games API using the RiotWatcher library.
# It requires the following dependencies: os, riotwatcher, dotenv.

import os
from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv('RIOT_API_KEY')

# Check that API key was loaded correctly
if api_key is None:
    raise Exception('Could not load RIOT_API_KEY from .env file')

# Create LolWatcher instance with API key
lol_watcher = LolWatcher(api_key)

# Specify region
region = 'na1'

try:
    # Query user
    user = lol_watcher.summoner.by_name(region, 'username')
    print(user)
    
except ApiError as err:
    if err.response.status_code == 429:
        print('We should retry in {} seconds.'.format(err.response.headers['Retry-After']))
        print('this retry-after is handled by default by the RiotWatcher library')
        print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
        print('Summoner with that ridiculous name not found.')
    else:
        raise
