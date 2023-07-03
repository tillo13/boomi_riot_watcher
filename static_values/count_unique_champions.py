import os
import json

match_dir = os.path.expanduser('matches')

champion_counts = {}
latest_file_with_champion = {}

for root, dirs, files in os.walk(match_dir):
    for filename in files:
        if filename.endswith('.json'):
            try:
                match = json.load(open(os.path.join(root, filename), 'r'))

                for participant in match['info']['participants']:
                    championId = participant['championId']

                    if championId not in champion_counts:
                        champion_counts[championId] = 1  # first time seeing this championId
                    else:
                        champion_counts[championId] += 1  # increment count

                    # Update the latest file for this championId
                    latest_file_with_champion[championId] = filename

            except json.JSONDecodeError:
                print(f"Skipped file {filename} due to JSON decoding error")

# Print the results
for championId, count in champion_counts.items():
    latest_file = latest_file_with_champion[championId]
    print(f"ChampionId {championId} occurs {count} times, last seen in file {latest_file}")