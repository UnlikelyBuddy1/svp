from math import radians, cos
import matplotlib.pyplot as plt
import pandas as pd

def plot_image(df):
    # Group by tiles and id, then count unique users per tile
    unique_users = df.groupby(['lat_tile', 'lon_tile', 'id']).size().reset_index(name='entries')
    tile_counts = unique_users.groupby(['lat_tile', 'lon_tile']).size().reset_index(name='unique_users')

    plt.figure(figsize=(10, 6))
    plt.scatter(tile_counts['lat_tile'], tile_counts['lon_tile'], c=tile_counts['unique_users'], cmap='viridis', s=100)
    plt.colorbar(label='Number of unique users')

    # Set axis limits to zoom into the data points area
    plt.xlim([min(tile_counts['lat_tile']) - 0.1, max(tile_counts['lat_tile']) + 0.1])
    plt.ylim([min(tile_counts['lon_tile']) - 0.1, max(tile_counts['lon_tile']) + 0.1])
    
    plt.xlabel('Latitude Tile (°)')
    plt.ylabel('Longitude Tile (°)')
    plt.title('Unique User Distribution Across Locations')
    plt.show()
