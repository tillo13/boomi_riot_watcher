import os
import json
import pandas as pd
import datetime

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif isinstance(x, list):
            for i, a in enumerate(x):
                flatten(a, name + str(i) + '_')
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

output_filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
user_folder = 'matches'

os.makedirs(user_folder, exist_ok=True)

subfolders_exist = False

for foldername in os.listdir(user_folder):
    folder_path = os.path.join(user_folder, foldername)
    if os.path.isdir(folder_path):
        subfolders_exist = True
        df = pd.DataFrame()

        for json_filename in os.listdir(folder_path):
            if json_filename.endswith(".json"):
                try:
                    with open(os.path.join(folder_path, json_filename)) as f:
                        data = json.load(f)
                        flat_data = flatten_json(data)
                        temp_df = pd.json_normalize(flat_data)
                        df = pd.concat([df, temp_df], ignore_index=True)
                except Exception as e:
                    print(f"Failed to process file {json_filename}. Reason: {e}")

        if not df.empty:
            csv_filename = f"{foldername}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
            csv_filepath = os.path.join(user_folder, csv_filename)
            df.to_csv(csv_filepath, index=False)
            print(f"Successfully converted {folder_path} to {csv_filepath}")
        else:
            print(f"No JSON files found in {folder_path}")

if not subfolders_exist:
    print(f"No subfolders found in '{user_folder}'.")

print(f"All subfolders in '{user_folder}' have been successfully converted to CSV files.")
