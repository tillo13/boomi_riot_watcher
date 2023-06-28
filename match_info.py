from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv
import os

load_dotenv()

lol_watcher = LolWatcher(os.getenv('RIOT_API_KEY'))

my_region = 'na1'

me = lol_watcher.summoner.by_name(my_region, 'cardyflower')

my_matches = lol_watcher.match.matchlist_by_puuid(my_region, me['puuid'])

aram_matches = []

# Fetch match details and check if it's an ARAM match (queueId == 450)
for match_id in my_matches:
    match_details = lol_watcher.match.by_id(my_region, match_id)
    if match_details['info']['queueId'] == 450:
        aram_matches.append(match_details)

# If ARAM matches were found, print the details of the first one
if aram_matches:
    first_aram_match_details = aram_matches[0]
    print(first_aram_match_details)
else:
    print("No ARAM matches found.")
