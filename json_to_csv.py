# This script converts multiple riot API league JSON files into a single CSV file.
# It requires the following dependencies: pandas, os, json, sys, datetime.

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

if len(sys.argv) > 1:
    output_filename = sys.argv[1]
    user_folder = sys.argv[2].replace(" ", "_").lower()  
else:
    output_filename = "default.csv"
    user_folder = 'defaulttest'

    os.makedirs(os.path.join("matches", user_folder), exist_ok=True)
    
    test_data = {
      "name": "John",
      "age": 30,
      "cars": {
        "car1": "Ford",
        "car2": "BMW",
        "car3": "Fiat"
      }
     } 

    with open(os.path.join("matches", user_folder, "test.json"), 'w') as f:
        json.dump(test_data, f)

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

df.to_csv(os.path.join(directory, output_filename), index=False)

print(f"All .json files have been successfully converted into a single .csv file named {output_filename} in the {directory} directory.")