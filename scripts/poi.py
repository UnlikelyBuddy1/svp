import pandas as pd

def generate_markov_chain(df, time_interval=60):
    """
    Generate a Markov chain matrix for user movement.
    Parameters:
    - df: DataFrame containing user movements with columns 'lat_tile', 'lon_tile', and 'timestamp'
    - time_interval: Integer representing the granularity of the time in minutes.
    Returns:
    - transition_matrix: A transition matrix representing the Markov chain.
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Reference start time
    start_time = df['timestamp'].min()
    # Compute the Time_period
    df['Time_period'] = ((df['timestamp'] - start_time).dt.total_seconds() // (time_interval * 60)).astype(int)
    # Create a composite state
    df['State'] = df['lat_tile'].astype(str) + "," + df['lon_tile'].astype(str) + "," + df['Time_period'].astype(str)
    # Calculate transitions
    transitions = df.sort_values(by='timestamp').groupby('id')['State'].shift(1) + "->" + df['State']
    transitions_counts = transitions.value_counts()
    # Convert to a matrix form for the Markov chain
    states = df['State'].unique().tolist()
    matrix_size = len(states)
    transition_matrix = pd.DataFrame(0, index=states, columns=states)
    for trans, count in transitions_counts.items():
        from_state, to_state = trans.split("->")
        if from_state in states and to_state in states:
            transition_matrix.at[from_state, to_state] = count
    # Normalize to get probabilities
    transition_matrix = transition_matrix.divide(transition_matrix.sum(axis=1), axis=0).fillna(0)
    return transition_matrix
