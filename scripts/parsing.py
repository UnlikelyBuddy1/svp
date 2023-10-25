import pandas as pd

ORIGINAL_SET_PATH = "../original/c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"
ANONYMIZED_SET_PATH = "../data/autofill_444_files/S_user_34_c046155c388437412a8755d2f980efb443817bc322e454409e6eeea89714302c"


def parse(path, n=None):
        df = pd.read_csv(path, nrows=n, sep='\t', names=["id", "timestamp", "lat", "lon"])
        return df[df.id != 'DEL']


def add_week_number(ds):
        print('input file loaded !')
        print('sorting weeks ...')
        ds['year_week'] = ds['timestamp'].apply(
                lambda date: str(pd.Timestamp(date).year) + '_' + str(pd.Timestamp(date).weekofyear))
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

data_frame = parse(ORIGINAL_SET_PATH, 100)
data_frame = add_week_number(data_frame)
save_per_week(data_frame)