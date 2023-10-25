import parsing
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from parsing import *
from graph import *

def heatmap(df):

    # Convert 'lat' and 'lon' to numeric data types
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    unique_users = df['id'].unique()
    #print(unique_users[0])
    for user_id in unique_users:
        user_data = df[df['id'] == user_id]
        
        # Print unique coordinates
        print(user_data.drop_duplicates(subset=['lat', 'lon']))

        #to_km_df = create_lat_lon_tiles(user_data)
        plot_heatmap(user_data, user_id)
    