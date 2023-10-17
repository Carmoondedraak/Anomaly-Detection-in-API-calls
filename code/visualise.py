import numpy as np
import matplotlib.pyplot as plt
from numpy import genfromtxt
import pandas as pd
import seaborn as sns
from tabulate import tabulate 
# from texttable import Texttable
import pickle
import os
import random
from scipy.stats import rankdata, norm


from category_encoders import *
from flows import *
from feature_encodings import *
from preprocessing import *
from visualising_dataset import *

def visualise_distribution(data_n,data_a, folder):
        
    data_n['target'] = 'normal'
    data_a['target'] = 'abnormal'

    # Concatenate the DataFrames
   
    combined_df = pd.concat([data_n, data_a])
    num_set = set(('content_length', 'time'))
    smallset = set(('response_code', 'response_line', 'request_method', 'x_forwarded_for', 'dst_p', 'cache_control','server','src','authbasic'))
    long_set = set(('src_p', 'request_uri_query','dst', 'request_uri')) #'file_data'
    medium_set = set(('user_agent','content_type','referer','authorization', 'cookie'))
    for column in combined_df.columns:
        if column == 'target':
            pass
        elif column in smallset:
            combined_df[column] = combined_df[column].astype(str)
        elif column in medium_set:
            combined_df[column] = combined_df[column].astype(str).str[:6]
        elif column in num_set:
            combined_df[column] = combined_df[column].astype(float)
        else:
            combined_df[column] = combined_df[column].astype(str).str[:10]

    sety = smallset | medium_set | num_set       

    for i in range(len(list(sety))):
        fig = plt.plot(figsize=(10,40))
        feat = list(sety)[i]
        fig = sns.histplot(data=combined_df, x=feat, hue='target',kde=True,  color=sns.color_palette('pastel')[0])
        plt.tick_params(axis='x', rotation=90)
        for k, cont in enumerate(fig.containers):
            if k %2 == 0:
                fig.bar_label(cont,label_type='edge',color='red')
            else:
                fig.bar_label(cont,label_type='edge',color='black')
        plt.ylabel('Count')
        plt.subplots_adjust(bottom=0.15)
        plt.title('Distribution of categories for '+ feat)
        plt.savefig(folder + 'distribution_of_amount_of_each_feature_values'+str(i)+'.png', bbox_inches="tight")
        plt.clf()

def visualise_real_data(data, folder):
 

    for i,j in enumerate(data.columns):
        fig = plt.plot(figsize=(10,40))
        feat = j
        fig = sns.histplot(data=data, x=feat, kde=True,  color=sns.color_palette('pastel')[0])
        plt.tick_params(axis='x', rotation=90)
        for k, cont in enumerate(fig.containers):
            fig.bar_label(cont,label_type='edge',color='black')
        plt.ylabel('Count')
        plt.subplots_adjust(bottom=0.15)
        plt.title('Distribution of categories for '+ feat)
        plt.savefig(folder + 'real_distribution_of_category_per_feature'+str(i)+'.png', bbox_inches="tight")
        plt.clf()

if __name__=="__main__":
    # the parser
    parser = argparse.ArgumentParser(
                    prog='Data Visualisation',
                    description='',
                    epilog='Text at the bottom of help')

    parser.add_argument('filename',metavar= 'filename of real dataset')           # positional argument
    parser.add_argument('filename1',metavar= 'filename of normal dataset')
    parser.add_argument('filename2',metavar= 'filename of abnormal dataset')
    parser.add_argument('savefolder', metavar= 'the file to save the prerocessed dataset')
    args = parser.parse_args()

    # load the preprocessed dataset
    data = pd.read_pickle(args.filename)
    data_n = pd.read_pickle(args.filename1)
    data_a = pd.read_pickle(args.filename2)

    # create data preprocessing object
    print('length of normal data',len(data_n))
    print('length of abnormal data', len(data_a))
    print('length of real-world data', len(data))
    print('columns n', data_n.columns, len(data_n.columns))
    print('colummns a', data_a.columns, len(data_a.columns))
    print('columns r', data.columns, len(data.columns))
    # change the values to string and float formats

    visualise_real_data(data, args.savefolder)
    visualise_distribution(data_n,data_a, args.savefolder)