from math import radians, cos
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def process_coordinates_and_group(df, tile_size=0.1):
    # If the dataframe is empty, return an empty dataframe
    if df.empty:
        return df

    # Define Earth's radius
    R = 6371.0

    def convert_row(row):
        lat_rad = radians(row['lat'])
        lon_rad = radians(row['lon'])
        x = R * lon_rad * cos(lat_rad)
        y = R * lat_rad
        return pd.Series({'x': x, 'y': y})

    xy_coords = df.apply(convert_row, axis=1)
    df['x'] = xy_coords['x']
    df['y'] = xy_coords['y']

    df['x_tile'] = (df['x'] / tile_size).apply(int)
    df['y_tile'] = (df['y'] / tile_size).apply(int)

    tile_counts = df.groupby(['x_tile', 'y_tile']).size().reset_index(name='count')
    return tile_counts

def sort_by_timestamp(df):
     
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp')
        return df

def filter_by_timestamp(df, weeks=1):
        # Get the date of the first record
        start_date = df['timestamp'].iloc[0]
        end_date = start_date + pd.Timedelta(weeks=weeks)
        df_week = df[df['timestamp'] < end_date]
        return df_week

def plot_image(df, tile_size=0.5):
    plt.figure(figsize=(10, 6))
    plt.scatter(df['x_tile'], df['y_tile'], c=df['count'], cmap='viridis', s=100)
    plt.colorbar(label='Number of users')

    # Set axis limits to zoom into the data points area
    plt.xlim([min(df['x_tile']) - 1, max(df['x_tile']) + 1])
    plt.ylim([min(df['y_tile']) - 1, max(df['y_tile']) + 1])
    
    plt.xlabel(f'X Tile ({tile_size} km)')
    plt.ylabel(f'Y Tile ({tile_size} km)')
    plt.title('User Distribution Across Locations')
    plt.show()


def plot_for_period(df, period='day', tile_size=0.1):
        if period == 'minute':
                df['period'] = df['timestamp'].dt.minute
                max_periods = 60
        elif period == 'hour':
                df['period'] = df['timestamp'].dt.hour
                max_periods = 24
        elif period == 'day':
                df['period'] = df['timestamp'].dt.day
                max_periods = (df['timestamp'].max() - df['timestamp'].min()).days + 1
        else:
                raise ValueError("Invalid period. Choose either 'minute', 'day', or 'hour'.")
        fig, ax = plt.subplots(figsize=(10, 6))
        ims = []
        for i in range(max_periods):
                df_period = df[df['period'] == i]
                if not df_period.empty:
                        tile_counts = process_coordinates_and_group(df_period, tile_size)
                        scatter = ax.scatter(tile_counts['x_tile'], tile_counts['y_tile'], c=tile_counts['count'], cmap='viridis', s=100, animated=True)
                else:
                        scatter = ax.scatter([], [], c=[], cmap='viridis', s=100, animated=True)  # Empty scatter for frames with no data
                if not df_period.empty:
                        ax.set_xlim([min(df_period['x_tile']) - 1, max(df_period['x_tile']) + 1])
                        ax.set_ylim([min(df_period['y_tile']) - 1, max(df_period['y_tile']) + 1])
                if period == 'minute':
                        title = ax.set_title(f'User Distribution: Minute {i}')
                elif period == 'hour':
                        title = ax.set_title(f'User Distribution: Hour {i}')
                else:  # 'day'
                        title = ax.set_title(f'User Distribution: Day {i+1}')
                ims.append([scatter, title])
        ani = animation.ArtistAnimation(fig, ims, interval=200, blit=True, repeat_delay=1000)
        if not df.empty:  # Only show colorbar if there's any data
                plt.colorbar(scatter, ax=ax, label='Number of users')
        plt.show()
