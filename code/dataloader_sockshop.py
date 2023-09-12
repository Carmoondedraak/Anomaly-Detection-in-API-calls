################################################################################
# MIT License
#
# Copyright (c) 2022
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to conditions.
#
# Author: Deep Learning Course | Autumn 2022
# Date Created: 2022-11-25
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


class Data(Dataset):
    def __init__(self, dirr, transform=None, target_transform=None):
        self.data = pd.read_pickle()
        self.dirr = dirr
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.data.columns)

    def __getitem__(self, idx):
        x = self.data.iloc[idx].drop(columns='target').dropna()
        label = self.data.iloc[idx, 'target']
        if self.transform:
            x = self.transform(x)
        if self.target_transform:
            label = self.target_transform(label)
        return x, label

def sock_data(batch_size,num_workers,root, transform=ToTensor(), target_transform):
    names = ['train', 'val','test']
    filenames = [os.join(root, i) for i in names]
    trains_set = Data(filenames[0]), transform,target_transform)    
    val_set = Data(filenames[1], transform,target_transform)
    test_set = Data(filenames[2], transform,target_transform)
    train_dataloader =  DataLoader(train_set, batch_size=4,
                        shuffle=True, num_workers=0)
    val_dataloader =  DataLoader(val_set, batch_size=4,
                        shuffle=True, num_workers=0)
    test_dataloader =  DataLoader(test_set, batch_size=4,
                        shuffle=True, num_workers=0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Model hyperparameters
    parser.add_argument('dirrr', type=srting, help='dataset (train, val or test)')
    args = parser.parse_args()

    dataset = Data(args.dirr, transform=ToTensor())
    dataloader = DataLoader(transformed_dataset, batch_size=4,
                        shuffle=True, num_workers=0)
