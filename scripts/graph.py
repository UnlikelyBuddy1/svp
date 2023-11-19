import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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


def plot_markov_chain_simple(transition_matrix, threshold=0.05):
    """
    Plot the Markov chain transitions using only matplotlib.
    Parameters:
    - transition_matrix: A pandas DataFrame representing the Markov chain transition matrix.
    - threshold: A float representing the minimum probability for an arrow to be drawn.
    Returns:
    None
    """
    n_states = transition_matrix.shape[0]
    fig, ax = plt.subplots(figsize=(12, 12))
    # Create grid positions for states
    positions = np.linspace(0, 1, n_states)
    state_positions = dict(zip(transition_matrix.index, positions))
    # Draw state points
    for state, pos in state_positions.items():
        ax.plot(pos, pos, 'o', markersize=10, label=state)
    # Draw transitions
    for from_state in transition_matrix.index:
        for to_state in transition_matrix.columns:
            probability = transition_matrix.at[from_state, to_state]
            if probability > threshold:
                # Use alpha for arrow to indicate transition probability
                alpha_val = probability
                ax.annotate("", 
                            xy=(state_positions[to_state], state_positions[to_state]), 
                            xytext=(state_positions[from_state], state_positions[from_state]), 
                            arrowprops=dict(arrowstyle="->", alpha=alpha_val))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(loc="best")
    ax.set_title("Markov Chain Transition Diagram")
    plt.show()


def plot_markov_chain_heatmap(transition_matrix):
    """
    Plot the Markov chain transitions as a heatmap using only matplotlib.
    Parameters:
    - transition_matrix: A pandas DataFrame representing the Markov chain transition matrix.
    Returns:
    None
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    # Use the imshow function of matplotlib to create the heatmap
    cax = ax.imshow(transition_matrix, cmap='viridis', interpolation='nearest')
    # Set labels and ticks based on states
    states = transition_matrix.index
    ax.set_xticks(np.arange(len(states)))
    ax.set_yticks(np.arange(len(states)))
    ax.set_xticklabels(states, rotation=45, ha='right')
    ax.set_yticklabels(states)
    # Add a colorbar to show the scale
    cbar = fig.colorbar(cax)
    cbar.set_label('Transition Probability')
    ax.set_title("Markov Chain Transition Heatmap")
    plt.tight_layout()
    plt.show()



def plot_heatmap(df, user_id):

    if hasattr(df, 'lat_tile'):
        tile_counts = df.groupby(['lat_tile', 'lon_tile']).size().reset_index(name='count')
    else:
        tile_counts = df.groupby(['lat', 'lon']).size().reset_index(name='count')

    # Merge tile_counts back into df
    df = df.merge(tile_counts, on=['lat', 'lon'])

    # Sort the DataFrame by 'count' in descending order to put in evidence the high-density points
    df = df.sort_values(by='count', ascending=True)

    plt.figure(figsize=(10, 6))
    plt.scatter(df['lat'], df['lon'], c=df['count'], cmap='viridis', s=100)
    
    plt.colorbar(label='Density')
    
    #plt.xlim([min(df['lat_tile']) - 0.1, max(df['lat_tile']) + 0.1])
    #plt.ylim([min(df['lon_tile']) - 0.1, max(df['lon_tile']) + 0.1])

    plt.ylim([40.00, 50.00])
    plt.xlim([0.00, 10.00])
    
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.title(f'Heatmap of user {user_id}')
    plt.show()
    
    print(max(df['count']))
