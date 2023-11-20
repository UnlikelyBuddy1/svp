import collections
import json
import os
from collections import defaultdict

import pandas as pd

OUTPUT_FOLDER = "./output"
SIMILARITY_LOG = OUTPUT_FOLDER + "/similarities";
ATTACK_RES_OUTPUT = OUTPUT_FOLDER + "/attack.json"


def parse(path, n=None):
    df = pd.read_csv(path, nrows=n, sep='\t', names=["id", "timestamp", "lat", "lon"])
    return df[df.id != 'DEL']


def add_week_number(ds):
    print('input file loaded !')
    print('sorting weeks ...')
    ds['year_week'] = ds['timestamp'].apply(
        lambda date: str(pd.Timestamp(date).year) + '-' + str(pd.Timestamp(date).weekofyear))
    ds['timestamp'] = pd.to_datetime(ds['timestamp'], format='%Y-%m-%d %H:%M:%S')
    ds.sort_values(by='timestamp', inplace=True)
    print('sorted weeks !')
    return ds


def save_per_week(ds, output_folder="./output/original/weeks"):
    import os
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Get unique weeks
    unique_weeks = ds['year_week'].unique()
    # Save each week to a separate file
    for week in unique_weeks:
        week_ds = ds[ds['year_week'] == week]
        output_filename = os.path.join(output_folder, f"data_{week}.csv")
        week_ds.to_csv(output_filename, index=False)
        print(f"Saved {output_filename}!")
    return


def create_lat_lon_tiles(df, lat_precision=0.1, lon_precision=0.1):
    df['lat_tile'] = (df['lat'] / lat_precision).apply(int) * lat_precision
    df['lon_tile'] = (df['lon'] / lon_precision).apply(int) * lon_precision
    return df


def separate_users(df):
    user_dict = {}
    for user_id, user_df in df.groupby('id'):
        user_dict[user_id] = user_df
    return user_dict

def log_similarity(input=
                    {
                    "2023-09":
                    {
                        "matches": [
                            {
                                "og_id": 1,
                                "anon_id": 664,
                                "similarity": 0.43
                            },
                            {
                                "og_id": 2,
                                "anon_id": 461,
                                "similarity": 0.24
                            },
                            {
                                "og_id": 4,
                                "anon_id": 98,
                                "similarity": 0.58
                            }
                        ]
                   }}):
    
    # Serializing json
    json_object = json.dumps(input, indent=4)

    # Ensure the output folder exists
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # If the file is not empty, we remove the last }
    if(os.path.exists(SIMILARITY_LOG) and os.stat(SIMILARITY_LOG).st_size != 0):
        with open(SIMILARITY_LOG, "rb+") as outfile:
            outfile.seek(-1, 2) 
            outfile.truncate() 
 
    with open(SIMILARITY_LOG, "a") as outfile:
        # If file is not empty, we add a , and we remove the first { of the new input
        if(os.stat(SIMILARITY_LOG).st_size != 0):
            outfile.write(",\n")
            outfile.write(json_object[1:])
        else:
            outfile.write(json_object)


def parse_to_json():

    f = open(SIMILARITY_LOG)
    data = json.load(f)

    d = {}
    for week in data:
        id = 0
        similarity = {}
        for user_id in data[week]["matches"]:
            #print(user_id)
            #print(str(data[week]["matches"][id]['og_id']) + ": " + str(data[week]["matches"][id]['anon_id']))
            similarity[data[week]["matches"][id]["og_id"]] = [data[week]["matches"][id]['anon_id']]
            id += 1
        d[week] = similarity
    print(d)

    # d = {
    #     "2015-10": {
    #         1: [83289621],
    #         6: [13381659],
    #         8: [31198199],
    #         16: [4814176],
    #         17: [87982896]
    #     },
    #     "2015-11": {
    #         1: [84256509],
    #         2: [47407364],
    #         6: [60544422],
    #         8: [86366129]
    #     },
    #     "2015-12": {
    #         1: [4646325],
    #         2: [63022696],
    #         6: [16235556],
    #         8: [62581893],
    #         13: [1014649],
    #         15: [24708159]
    #     }
    # }

    # Put duplicates anon_id in a grouped set like this :
    # { 1 : 664 }, {1 : 665 } ===> { 1 : [664,665] }
    res_dict = defaultdict(dict)

    for week in d:
        week_dict = d[week]
        week_str = str(week)
        for find_id in week_dict:
            possible_users = week_dict[find_id]
            find_id_str = str(find_id)
            possible_users_str = [str(possible_user) for possible_user in possible_users]
            res_dict[find_id_str].update({week_str: possible_users_str})

    # Ensure the output folder exists
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Save json
    output_filename = os.path.join(ATTACK_RES_OUTPUT)
    with open(output_filename, 'w+') as f:
        json.dump(res_dict, f)
    print(f"Saved {ATTACK_RES_OUTPUT}!")

