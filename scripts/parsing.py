import pandas as pd
import numpy as np

ORIGINAL_SET_PATH = "original/c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"

def parse(path, n=1000):
        return pd.read_csv(path, nrows=n, sep='\t' , names=["id", "timestamp", "lat", "lon"])


og = parse(ORIGINAL_SET_PATH)
og['lat'].plot(kind='hist')