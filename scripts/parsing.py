from datetime import datetime

import pandas as pd
import numpy as np

ORIGINAL_SET_PATH = "../data/original/c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"
ANONYMIZED_SET_PATH = "../data/autofill_444_files/S_user_34_c046155c388437412a8755d2f980efb443817bc322e454409e6eeea89714302c"


def parse(path, n=100):
    df = pd.read_csv(path, nrows=n, sep='\t', names=["id", "timestamp", "lat", "lon"])
    return df[df.id != 'DEL']


dSource = parse(ORIGINAL_SET_PATH)

dSource['year_week'] = dSource['timestamp'].apply(
    lambda date: str(pd.Timestamp(date).year) + '_' + str(pd.Timestamp(date).weekofyear))
dSource['timestamp'] = pd.to_datetime(dSource['timestamp'], format='%Y-%m-%d %H:%M:%S')
dSource.sort_values(by='timestamp', inplace=True)

print(dSource.to_markdown() + '\n')

dTarget = parse(ANONYMIZED_SET_PATH)

dTarget['year_week'] = dTarget['timestamp'].apply(
    lambda date: str(pd.Timestamp(date).year) + '_' + str(pd.Timestamp(date).weekofyear))
dTarget['timestamp'] = pd.to_datetime(dTarget['timestamp'], format='%Y-%m-%d %H:%M:%S')
dTarget.sort_values(by='timestamp', inplace=True)

print(dTarget.to_markdown() + '\n')

ids_source = pd.unique(dSource["id"])
print(ids_source)
ids_target = pd.unique(dTarget["id"])
print(ids_target)

year_weeks = pd.unique(dSource["year_week"])
print('year_weeks : ' + year_weeks)

res = {}
for wy in year_weeks:
    ids = pd.unique(dTarget[dTarget['year_week'] == wy]['id'])
    for i in ids:
        print(f"{wy} {i}")
