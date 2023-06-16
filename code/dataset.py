import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import pandas as pd
import seaborn as sns
from tabulate import tabulate 
from texttable import Texttable
import pickle
import os
import random

class Dataset():
    def load_in_files(self):
    data_n = pd.read_pickle('../Dataset/Normal/normal_dataset.pkl')
    data_a = pd.read_pickle('../Dataset/Anomalies/anom.pkl')
    return data_n, data_a

if __name__=="__main__":
    data_n, data_a = load_in_files()
