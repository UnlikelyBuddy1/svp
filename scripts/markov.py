import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from scipy.optimize import linear_sum_assignment
import json
from multiprocessing import Pool

coordonate_precision = 0.01
time_interval = 15
class Parser:
    def __init__(self, path):
        self.path = path
        self.df = self.parse(self.path)   
    def parse(self, path, n=None):
        df = pd.read_csv(path, nrows=n, sep='\t', names=["id", "timestamp", "lat", "lon"])
        return df[df.id != 'DEL']
    def processWeeks(self, output_folder="./output/original/weeks"):
        print('input file loaded !')
        print('sorting weeks ...')
        self.df['year_week'] = self.df['timestamp'].apply(
            lambda date: str(pd.Timestamp(date).year) + '-' + str(pd.Timestamp(date).weekofyear))
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], format='%Y-%m-%d %H:%M:%S')
        self.df.sort_values(by='timestamp', inplace=True)
        print('sorted weeks !')
        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        # Get unique weeks
        unique_weeks = self.df['year_week'].unique()
        # Save each week to a separate file
        for week in unique_weeks:
            week_ds = self.df[self.df['year_week'] == week]
            output_filename = os.path.join(output_folder, f"data_{week}.csv")
            week_ds.to_csv(output_filename, index=False)
            print(f"Saved {output_filename}!")
    
class DatasetWeek:
    def __init__(self, path):
        data = pd.read_csv(path, sep=',')
        tiled_week_frame = self.createTiles(data, coordonate_precision)
        users_dict = self.separateUsers(tiled_week_frame)
        self.users = []
        for user_id, user_df in users_dict.items():
            self.users.append(User(user_id, user_df))
    def createTiles(self, df, coordonate_precision):
        df['lat_tile'] = (df['lat'] / coordonate_precision).apply(int) * coordonate_precision
        df['lon_tile'] = (df['lon'] / coordonate_precision).apply(int) * coordonate_precision * 2
        return df
    def separateUsers(self, df):
        user_dict = {}
        for user_id, user_df in df.groupby('id'):
            user_dict[user_id] = user_df
        return user_dict

class User: 
    def __init__(self, id, df):
        self.id = id
        self.df = df
        self.matrix = self.createTransitionMatrix(self.df)
    def createTransitionMatrix(self, df):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        start_time = df['timestamp'].min()
        df['Time_period'] = ((df['timestamp'] - start_time).dt.total_seconds() // (time_interval * 60)).astype(int)
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

class DatasetComparator:
    def __init__(self, pathOG, pathANON):
        self.datasetOG = DatasetWeek(pathOG)
        self.datasetANON = DatasetWeek(pathANON)
        self.bestMatches = []
    def compare(self, userA, userB):
        states = userA.matrix.index.union(userB.matrix.index)
        matrixA = userA.matrix.reindex(index=states, columns=states, fill_value=0)
        matrixB = userB.matrix.reindex(index=states, columns=states, fill_value=0)
        diff = np.linalg.norm(matrixA.to_numpy() - matrixB.to_numpy(), 'fro')
        max_diff = np.linalg.norm(np.ones(matrixA.shape), 'fro')
        if max_diff == 0:
            return 0
        return 1 - diff / max_diff
    def compareAllUsers(self, best_n=None):
        print(f"Matching {len(self.datasetOG.users)} users from original dataset with {len(self.datasetANON.users)} users from anonymized dataset...")
        matches = []
        for userA in self.datasetOG.users:
            user_matches = []
            for userB in self.datasetANON.users:
                result = {}
                result["anon"] = userB.id
                result["similarity"] = self.compare(userA, userB)
                user_matches.append(result)
            user_matches.sort(key=lambda x: x["similarity"], reverse=True)
            user_result = {}
            user_result["original"] = userA.id
            user_result["best_matches"] = user_matches[:best_n]
            matches.append(user_result)
        return matches
    def findBestMatches(self):
        num_original = len(self.datasetOG.users)
        num_anon = len(self.datasetANON.users)
        cost_matrix = np.zeros((num_original, num_anon))
        cost_matrix = np.nan_to_num(cost_matrix, nan=np.inf)
        for i, userA in enumerate(self.datasetOG.users):
            for j, userB in enumerate(self.datasetANON.users):
                cost_matrix[i, j] = 1 - self.compare(userA, userB)
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        matches = []
        for i, j in zip(row_ind, col_ind):
            original_id = self.datasetOG.users[i].id
            anon_id = self.datasetANON.users[j].id
            similarity = 1 - cost_matrix[i, j]
            matches.append({'original': original_id, 'anon': anon_id, 'similarity': similarity})
        result = {}
        result["week"] = self.datasetOG.users[0].df['year_week'].iloc[0]
        result["matches"] = matches
        self.bestMatches = result
        return result
    def formatJSON(self):
        week = self.bestMatches['week']
        matches = self.bestMatches['matches']
        formatted_results = {}
        for match in matches:
            original = match['original']
            anon = match['anon']
            # Initialize original user's dict if not present
            if original not in formatted_results:
                formatted_results[original] = {}
            # Assign the anon to the corresponding week under the original user
            if week not in formatted_results[original]:
                formatted_results[original][week] = []
            formatted_results[original][week].append(anon)
        return formatted_results

def process_week(original_path, anon_path):
    print(f"Comparing {original_path} with {anon_path}...")
    comparator = DatasetComparator(original_path, anon_path)
    comparator.findBestMatches()
    return comparator.formatJSON()

def merge_results(results):
    merged = {}
    for week_result in results:
        for original, week_data in week_result.items():
            if original not in merged:
                merged[original] = {}

            for week, anon_list in week_data.items():
                if week in merged[original]:
                    merged[original][week].extend(anon_list)
                else:
                    merged[original][week] = anon_list
    return merged

def attack(original_dir, anon_dir):
    file_paths = [(os.path.join(original_dir, f), os.path.join(anon_dir, f))
                  for f in os.listdir(original_dir) if f.endswith(".csv")]
    with Pool() as pool:
        results = pool.starmap(process_week, file_paths)
    print("Merging results...")
    merged_results = merge_results(results)
    output_JSON = json.dumps(merged_results, indent=4)
    with open('output.json', 'w') as file:
        file.write(output_JSON)
    return output_JSON

if __name__ == '__main__':
    start_time = pd.Timestamp.now()
    output_JSON = attack("./output/original/weeks", "./output/anon/weeks")
    end_time = pd.Timestamp.now()
    print(f"Finished in {(end_time - start_time).total_seconds()} seconds.")