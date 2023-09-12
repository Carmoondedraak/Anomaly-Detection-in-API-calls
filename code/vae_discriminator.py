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
# Author: 
# Date Created: 2023-09-18
################################################################################

import argparse
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.utils import make_grid, save_image
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint

from mnist import mnist
from encoder_decoder import Encoder, Decoder, Discriminator
from utils import *


class VAE(pl.LightningModule):

    def __init__(self, num_filters, z_dim, lr):
        """
        PyTorch Lightning module that summarizes all components to train a VAE.
        Inputs:
            num_filters - Number of channels to use in a CNN encoder/decoder
            z_dim - Dimensionality of latent space
            lr - Learning rate to use for the optimizer
        """
        super().__init__()
        self.save_hyperparameters()
        self.encoder = Encoder(z_dim=z_dim, num_filters=num_filters)
        self.decoder = Decoder(z_dim=z_dim, num_filters=num_filters)
        self.discriminator = Discriminator(z_dim=z_dim, num_filters=num_filters)
        self.zdim = z_dim
        self.softmax = nn.Softmax()
        # self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

    def forward(self, x):
        """
        The forward function calculates the VAE-loss for a given batch of images.
        Inputs:
            imgs - Batch of images of shape [B,C,H,W].
                   The input images are converted to 4-bit, i.e. integers between 0 and 15.
        Ouptuts:
            L_rec - The average reconstruction loss of the batch. Shape: single scalar
            L_reg - The average regularization loss (KLD) of the batch. Shape: single scalar
            bpd - The average bits per dimension metric of the batch.
                  This is also the loss we train on. Shape: single scalar
        """

        # Hints:
        # - Implement the empty functions in utils.py before continuing
        # - The forward run consists of encoding the images, sampling in
        #   latent space, and decoding.
        # - By default, torch.nn.functional.cross_entropy takes the mean accross
        #   all axes. Do not forget to change the 'reduction' parameter to
        #   make it consistent with the loss definition of the assignment.

        batch_size = x.shape[0]
        loss = nn.CrossEntropyLoss(reduction='sum')
        mean, log_std = self.encoder(x)

        z_samples = sample_reparameterize(mean, torch.exp(log_std)).to(self.device)
        out = self.decoder(z_samples)
        L_rec = loss(out, x.reshape(batch_size,28,28)) / x.shape[0]
        L_reg = torch.mean(KLD(mean,log_std))
        elbo = L_rec - L_reg
        bpd = torch.mean(elbo_to_bpd(elbo, x.shape))

        return L_rec, L_reg, bpd

        @torch.no_grad()
    def sample(self, batch_size):
        """
        Function for sampling a new batch of random images.
        Inputs:
            batch_size - Number of images to generate
        Outputs:
            x_samples - Sampled, 4-bit images. Shape: [B,C,H,W]
        """
        z = torch.randn(size=(batch_size,self.zdim)).to(self.device)
        out = self.softmax(self.decoder(z))
        batch = out.reshape(batch_size*28*28,16)
        x_samples = torch.multinomial(batch,1).reshape(batch_size,1,28,28)
        return x_samples

    def configure_optimizers(self):
        # Create optimizer
        optimizer = torch.optim.Adam(self.parameters(), lr=self.hparams.lr)
        return optimizer

    def training_step(self, batch, batch_idx):
        # Make use of the forward function, and add logging statements
        L_rec, L_reg, bpd = self.forward(batch[0])
        self.log("train_reconstruction_loss", L_rec, on_step=False, on_epoch=True)
        self.log("train_regularization_loss", L_reg, on_step=False, on_epoch=True)
        self.log("train_ELBO", L_rec + L_reg, on_step=False, on_epoch=True)
        self.log("train_bpd", bpd, on_step=False, on_epoch=True)

        return bpd

    def validation_step(self, batch, batch_idx):
        # Make use of the forward function, and add logging statements
        L_rec, L_reg, bpd = self.forward(batch[0])
        self.log("val_reconstruction_loss", L_rec)
        self.log("val_regularization_loss", L_reg)
        self.log("val_ELBO", L_rec + L_reg)
        self.log("val_bpd", bpd)

    def test_step(self, batch, batch_idx):
        # Make use of the forward function, and add logging statements
        L_rec, L_reg, bpd = self.forward(batch[0])
        self.log("test_bpd", bpd)