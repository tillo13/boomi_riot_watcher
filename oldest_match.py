from riotwatcher import LolWatcher, ApiError
from dotenv import load_dotenv
import os, time

load_dotenv()

lol_watcher = LolWatcher(os.getenv('RIOT_API_KEY'))

my_region = 'na1'
summoner_name = 'cardyflower'

# Get the summoner details to obtain the PUUID
try:
    summoner = lol_watcher.summoner.by_name(my_region, summoner_name)
    puuid = summoner['puuid']

    oldest_match_id = None
    oldest_match_timestamp = float('inf')  # Start with a very high timestamp

    start_index = 0
    count = 100  # Get maximum number of matches per request

    total_matches = 0
    print('Processing matches...')

    while True:
        try:
            matchlist = lol_watcher.match.matchlist_by_puuid(my_region, puuid, start=start_index, count=count)

            for match_id in matchlist:
                match = lol_watcher.match.by_id(my_region, match_id)

                # Update the oldest match timestamp if necessary
                if match['info']['gameCreation'] < oldest_match_timestamp:
                    oldest_match_timestamp = match['info']['gameCreation']
                    oldest_match_id = match_id

                total_matches += 1

            start_index += count

        except ApiError as err:
            if err.response.status_code == 429:
                print('We hit a rate limit error, waiting for 120 seconds before retrying...')
                time.sleep(120)
            else:
                raise err

        if len(matchlist) < count:
            # Reached the end of matchlist
            break

    # Convert the oldest match timestamp to a human-readable format
    oldest_match_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(oldest_match_timestamp/1000))

    print(f"The oldest gameCreation in the API for {summoner_name} is: {oldest_match_date}")
    print(f"Total matches processed: {total_matches}")

except ApiError as err:
    print(f"An error occurred: {err}")
