import pandas as pd
import os
import json
import sys
import datetime

default_time = datetime.datetime.now()
default_timestamp = default_time.strftime("%Y_%m_%d_%H_%M_%S")

if len(sys.argv) > 1:
    output_filename = sys.argv[1]
    # Retrieve summoner_name from sys.argv
    user_folder = sys.argv[2].replace(" ","_").lower()  #convert name to lowercase
else:
    output_filename = f"default_{default_timestamp}.csv"
    user_folder = 'default'

directory = "matches"
df = pd.DataFrame()

for json_filename in os.listdir(directory):
    if json_filename.endswith(".json"):
        with open(os.path.join(directory, json_filename)) as f:
            data = json.load(f)

            # Flatten nested fields
            for p_index, p in enumerate(data['info']['participants']):
                for challenge_key, challenge_value in p.get('challenges', {}).items():
                    p[f'challenges.{challenge_key}'] = challenge_value

                for perk_style in p.get('perks', {}).get('styles', []):
                    p[f'perks.styles.{perk_style["description"]}'] = perk_style['style']
                    for perk in perk_style.get('selections', []):
                        p[f'perks.styles.{perk_style["description"]}.selections.{perk["perk"]}'] = perk['var1'], perk['var2'], perk['var3']

            for stat_perks_key, stat_perks_value in p.get('perks', {}).get('statPerks', {}).items():
                p[f'perks.statPerks.{stat_perks_key}'] = stat_perks_value

            # Replace the original participant data with flattened data 
            data['info']['participants'][p_index] = p

        # Normalize here at this level before moving onto the next file.
        temp_df = pd.json_normalize(data, record_path=['info', 'participants'])
        df = pd.concat([df, temp_df], ignore_index=True)

output_dir = os.path.join(directory, user_folder)
os.makedirs(output_dir, exist_ok=True)
output_filepath = os.path.join(output_dir, output_filename)
df.to_csv(output_filepath, index=False)

print(f"All .json files have been successfully converted into a single .csv file named {output_filename} in the {directory} directory.")
