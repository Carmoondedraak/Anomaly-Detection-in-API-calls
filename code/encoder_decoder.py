
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
# Date Created: 2023-09-11
################################################################################

import torch
import torch.nn as nn
import numpy as np
import argparse
import os
import random
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from IPython.display import HTML

# Set random seed for reproducibility
manualSeed = 999
#manualSeed = random.randint(1, 10000) # use if you want new results
print("Random Seed: ", manualSeed)
random.seed(manualSeed)
torch.manual_seed(manualSeed)
torch.use_deterministic_algorithms(True) # Needed for reproducible results


class Encoder(nn.Module):
    def __init__(self, num_features,num_filters, z_dim):
        super(Encoder,self).__init__()
        # self.ngpu = ngpu
        self.net = nn.Sequential(
            nn.Conv1d(1,num_filters, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm1d(num_filters),
            nn.LeakyReLU(0.1),            
            
            # state size. 
            nn.Conv1d(num_filters, num_filters * 2, kernel_size=3, stride=2, padding=1,bias=False),
            nn.BatchNorm1d(num_filters*2),
            nn.LeakyReLU(0.1),

            # state size. 
            nn.Conv1d(num_filters * 2, num_filters * 2, kernel_size=3, stride=1, padding=0,bias=False),
            nn.LeakyReLU(0.1),

            nn.Flatten()
        )
        self.linear1 = nn.Linear(num_filters *(((num_features-1)//2)-1)*2,z_dim)
        self.linear2 = nn.Linear(num_filters *(((num_features-1)//2)-1)*2,z_dim)

    def forward(self, input):
        x = self.net(input)
        # print('encoder input',x.shape)
        mean = self.linear1(x)
        log_std = self.linear2(x)
        return mean, log_std

class Decoder(nn.Module):
    def __init__(self, num_features,num_filters,z_dim):
        super(Decoder, self).__init__()
        # self.ngpu = ngpu
        self.num_features = num_features
        self.num_filters = num_filters
        self.linear = nn.Sequential(
            nn.Linear(z_dim, num_filters*2*(((num_features-1)//2)-1) ),
            nn.LeakyReLU(0.1)
        )
        self.net = nn.Sequential(
            # input is Z, going into a convolution 1
            nn.ConvTranspose1d(num_filters*2, num_filters * 2, kernel_size=3, stride=1, padding=0, bias=False),
            
            nn.LeakyReLU(0.1),
            nn.BatchNorm1d(num_filters*2 ),
            # state size. ``(ngf*8) x 4 x 4`` conv2
            nn.ConvTranspose1d(num_filters * 2, num_filters, kernel_size=3, stride=2, padding=1, bias=False),
            
            nn.LeakyReLU(0.1),
            nn.BatchNorm1d(num_filters),
            # state size. ``(num_filters*4) x 8 x 8`` conv3
            nn.ConvTranspose1d(num_filters,1, kernel_size=3, stride=1, padding=1, bias=False))
            # nn.BatchNorm1d(num_features * 2),
     

    def forward(self, input, batch_size):
        z = self.linear(input)
        # print('decoder',z.shape)
        z = z.reshape(batch_size,self.num_filters*2,((self.num_features-1)//2)-1) 

        new = self.net(z)
        return new

class Discriminator(nn.Module):
    def __init__(self, num_features,num_filters,z_dim):
        self.num_features = num_features
        super(Discriminator, self).__init__()
        # self.ngpu = ngpu
        self.net = nn.Sequential(

            nn.Conv1d(1, num_filters, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm1d(num_filters),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Conv1d(num_filters,num_filters *2, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm1d(num_filters*2 ),
            nn.LeakyReLU(0.2, inplace=True),
            
            nn.Conv1d(num_filters *2,num_filters*2, kernel_size=3, stride=1, padding=0, bias=False),
            # nn.BatchNorm1d(num_filters*2),
            nn.LeakyReLU(0.2, inplace=True),
        )
        self.dropout = nn.Sequential(
            nn.Flatten(),
            nn.Linear(num_filters *2*(((self.num_features-1)//2)-1),z_dim)
            )
        self.net2 = nn.Sequential(
            # nn.Conv1d(num_filters *2,1, kernel_size=3, stride=1, padding=0, bias=False),
            # nn.LeakyReLU(0.2,inplace=True),
            nn.Flatten(),
            nn.Linear(num_filters*2*(((self.num_features-1)//2)-1), 1), # Output layer with a single neuron
            nn.Sigmoid()
        )

    def forward(self, input, batch_size):
        # print('Discriminator',self.net)
        # print(input.shape)
        input = input.reshape(batch_size,1,self.num_features)
        new = self.net(input)
        output = self.dropout(new)
        new = self.net2(new)
        return new, output

