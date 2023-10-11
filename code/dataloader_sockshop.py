################################################################################
# MIT License
#
# Copyright (c) 2023
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to conditions.
#
# Author: Carmen Veenker
# Date Created: 2023-09-12
################################################################################

import torchvision
from torchvision import transforms
import torch
import torch.utils.data as data
from torch.utils.data import random_split
import numpy as np
from torch.utils.data import Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor
import matplotlib.pyplot as plt
import os
import pandas as pd
from flows import *
from feature_encodings import *
from preprocessing import *
from visualising_dataset import *
from torch.utils.data import DataLoader
from torch.nn.functional import normalize

class Data(Dataset):
    def __init__(self, dirr,filename, transform=None, target_transform=None):
        self.data = pd.read_pickle(dirr)
        self.targets= pd.read_pickle("/".join(dirr.split('/')[:-1]) + '/' + filename.split('.')[0]+  '_targets.pkl')
        self.dirr = dirr
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        label = self.targets.iloc[idx]
        x = self.data.iloc[idx].drop(columns='target').dropna()
        if self.transform:
            x = torch.tensor(x.values, dtype=torch.float)
            x = torch.nn.functional.normalize(x, p=2.0, dim = 0)
            x = x.reshape(1,len(x))
        if self.target_transform:
            label = torch.tensor(label, dtype=torch.float)
        return x, label

def sock_data(batch_size,num_workers,root, transform=ToTensor(), target_transform=False):
    names = ['train.pkl', 'val.pkl','test.pkl']
    filenames = [os.path.join(root, i) for i in names]
    train_set = Data(filenames[0],names[0], transform,target_transform)    
    val_set = Data(filenames[1],names[1], transform,target_transform)
    test_set = Data(filenames[2], names[2], transform,True)

    train_dataloader =  DataLoader(train_set, batch_size=batch_size,
                        shuffle=True, num_workers=0)
    val_dataloader =  DataLoader(val_set, batch_size=batch_size,
                        shuffle=True, num_workers=0)
    test_dataloader =  DataLoader(test_set,batch_size=batch_size,
                        shuffle=True, num_workers=0)
    return train_dataloader, val_dataloader, test_dataloader

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Model hyperparameters
    parser.add_argument('dirrr', type=str, help='dataset (train, val or test)')
    parser.add_argument('filename', type=str)
    parser.add_argument('filename1',type=str)
    args = parser.parse_args()

    data_n = pd.read_pickle(args.filename)
    data_a = pd.read_pickle(args.filename1)
    
    # categorical and numerical data defined
    categorical_feats = ['user_agent','response_line','cache_control', 'content_length','server','file_data','dst','src','src_p','dst_p','request_method','request_uri','request_uri_query','x_forwarded_for','user_agent','cookie','transfer_encoding','referer','authorization','authbasic','content_type','response_code']
    numerical = ['time']

    # create data preprocessing object
    data_preprocessor = Data_Preprocess(data_n,data_a)

    # change the values to string and float formats
    data_n = data_preprocessor.change_values(data_n,numerical,categorical_feats)
    data_a = data_preprocessor.change_values(data_a,numerical,categorical_feats)
    data = [data_n,data_a]
    filenames = ['~/Anomaly-Detection-in-API-calls/data/train.pkl', '~/Anomaly-Detection-in-API-calls/data/val.pkl','~/Anomaly-Detection-in-API-calls/data/test.pkl']
    filenames_t = ['~/Anomaly-Detection-in-API-calls/data/train_targets.pkl','~/Anomaly-Detection-in-API-calls/data/val_targets.pkl','~/Anomaly-Detection-in-API-calls/data/test_targets.pkl']
    encoder_obj = Encoders()
    encoders = encoder_obj.encoders

    splitter = Train_Val_Test_split(only_normal=True)
        
    if not os.path.exists(args.dirrr):
    # If it doesn't exist, create it
        os.makedirs(args.dirrr)
    
    encoder = 'cat'

    X_n = encoder_obj.choose_encoding(data[0],encoder)
    X_a = encoder_obj.choose_encoding(data[1],encoder)
    splitter.split_dataset([X_n,X_a])

    data = [splitter.train_set, splitter.val_set,splitter.test_set]
    targets = [splitter.train_targets, splitter.val_targets, splitter.test_targets]

    for i,names in enumerate(filenames):
        data_preprocessor.save_dataset(names, data[i], flag=True )
        data_preprocessor.save_dataset(filenames_t[i], targets[i],flag=True)


