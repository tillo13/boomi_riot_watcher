import pandas as pd
import os
import json
import sys
import datetime

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

default_time = datetime.datetime.now()
default_timestamp = default_time.strftime("%Y_%m_%d_%H_%M_%S")

if len(sys.argv) > 1:
    output_filename = sys.argv[1]
    user_folder = sys.argv[2].replace(" ", "_").lower()  
else:
    output_filename = f"default_{default_timestamp}.csv"
    user_folder = 'default'

directory = os.path.join("matches", user_folder)
df = pd.DataFrame()

for json_filename in os.listdir(directory):
    if json_filename.endswith(".json"):
        try:
            with open(os.path.join(directory, json_filename)) as f:
                data = json.load(f)
                flat_data = flatten_json(data)
                temp_df = pd.json_normalize(flat_data)
                df = pd.concat([df, temp_df], ignore_index=True)
        except Exception as e:  
            print(f"Failed to process file {json_filename}. Reason: {e}")

output_dir = directory
output_filepath = os.path.join(output_dir, output_filename)
df.to_csv(output_filepath, index=False)

print(f"All .json files have been successfully converted into a single .csv file named {output_filename} in the {directory} directory.")