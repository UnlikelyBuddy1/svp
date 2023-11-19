import collections
import json
import os
from collections import defaultdict

import pandas as pd


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


def parse_to_json(output_folder="./output/res"):
    d = {
        "2015-10": {
            1: [83289621],
            6: [13381659],
            8: [31198199],
            16: [4814176],
            17: [87982896]
        },
        "2015-11": {
            1: [84256509],
            2: [47407364],
            6: [60544422],
            8: [86366129]
        },
        "2015-12": {
            1: [4646325],
            2: [63022696],
            6: [16235556],
            8: [62581893],
            13: [1014649],
            15: [24708159]
        }
    }

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
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Save json
    output_filename = os.path.join(output_folder, f"attack.json")
    with open(output_filename, 'w+') as f:
        json.dump(res_dict, f)
    print(f"Saved {output_filename}!")
