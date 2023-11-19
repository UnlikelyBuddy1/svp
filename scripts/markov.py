import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class DatasetWeek: 
    def __init__(self, path, coordonate_precision, time_interval):
        data = pd.read_csv(path, sep=',')
        print(data)
        tiled_week_frame = self.create_lat_lon_tiles(data, coordonate_precision, coordonate_precision)
        users_dict = self.separate_users(tiled_week_frame)
        self.users = []
        for user_id, user_df in users_dict.items():
            self.users.append(User(user_id, user_df))
        
    def create_lat_lon_tiles(self, df, lat_precision=0.1, lon_precision=0.1):
        df['lat_tile'] = (df['lat'] / lat_precision).apply(int) * lat_precision
        df['lon_tile'] = (df['lon'] / lon_precision).apply(int) * lon_precision * 2
        return df
    def separate_users(self, df):
        user_dict = {}
        for user_id, user_df in df.groupby('id'):
            user_dict[user_id] = user_df
        return user_dict
    @staticmethod
    def compare(self, userA, userB):
        diff = np.linalg.norm(userA.transition.matrix.to_numpy() - userB.transition.matrix.to_numpy(), 'fro')
        max_diff = np.linalg.norm(np.ones(userA.transition.matrix.shape), 'fro')
        return 1 - diff / max_diff

class User: 
    def __init__(self, id, df):
        self.id = id
        self.df = df
        self.transition = UserTransitionMatrix(df)

class UserTransitionMatrix:
    def __init__(self, df=None, time_interval=15):
        self.time_interval = time_interval
        if df is not None:
            self.matrix = self.create(df)
        else :
            self.matrix = None
    def create(self, df):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        start_time = df['timestamp'].min()
        df['Time_period'] = ((df['timestamp'] - start_time).dt.total_seconds() // (self.time_interval * 60)).astype(int)
        df = df.sort_values(by='timestamp').groupby('Time_period').first().reset_index()

        # Count transitions
        df['current_state'] = df['lat_tile'].astype(str) + ',' + df['lon_tile'].astype(str)
        df['next_state'] = df.groupby('id')['current_state'].shift(-1)
        df = df.dropna(subset=['next_state'])
        transitions = df.groupby(['current_state', 'next_state']).size().reset_index(name='count')

        # Create transition matrix
        matrix = transitions.pivot(index='current_state', columns='next_state', values='count').fillna(0)
        matrix = matrix.div(matrix.sum(axis=1), axis=0)
        return matrix
    def plot(self):
        plt.figure(figsize=(10, 10))
        sns.heatmap(self.matrix, annot=False, cmap='viridis', fmt=".2f")
        plt.title('Transition Matrix Heatmap')
        plt.xlabel('Next State')
        plt.ylabel('Current State')
        plt.show()
    
week_data = DatasetWeek('./output/original/weeks/data_2015_18.csv', 0.001, 15)
print(week_data.users[5].transition.plot())