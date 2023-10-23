import pandas as pd
import numpy as np

def parse(path):
        return pd.read_csv(path, sep='\t' , names=["id", "timestamp", "lat", "lon"])

print(parse("original/c3465dad3864bb1e373891fdcfbfcca5f974db6a9e0b646584e07c5f554d7df7"))