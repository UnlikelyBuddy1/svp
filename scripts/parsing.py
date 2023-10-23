import pandas as pd
import numpy as np
from graph import *

ORIGINAL_SET_PATH = "../original/c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"

def parse(path, n=1000):
        return pd.read_csv(path, nrows=n, sep='\t' , names=["id", "timestamp", "lat", "lon"])


og = parse(ORIGINAL_SET_PATH, 1000000)
# df = sort_by_timestamp(og)
# df = filter_by_timestamp(df)
# plot_for_period(df,'hour', 0.1)

