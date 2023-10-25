import pandas as pd

ORIGINAL_SET_PATH = "../data/original/c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"
ANONYMIZED_SET_PATH = "../data/autofill_444_files/S_user_34_c046155c388437412a8755d2f980efb443817bc322e454409e6eeea89714302c"


def parse(path, n=100):
    df = pd.read_csv(path, nrows=n, sep='\t', names=["id", "timestamp", "lat", "lon"])
    return df[df.id != 'DEL']


def add_week_number(path):
    ds = parse(path)
    ds['year_week'] = ds['timestamp'].apply(
        lambda date: str(pd.Timestamp(date).year) + '_' + str(pd.Timestamp(date).weekofyear))
    ds['timestamp'] = pd.to_datetime(ds['timestamp'], format='%Y-%m-%d %H:%M:%S')
    ds.sort_values(by='timestamp', inplace=True)
    return ds


dSource = add_week_number(ORIGINAL_SET_PATH)
print(dSource.to_markdown() + '\n')

dTarget = add_week_number(ANONYMIZED_SET_PATH)
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
