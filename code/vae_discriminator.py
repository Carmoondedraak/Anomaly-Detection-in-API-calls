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
from torchmetrics.regression import KLDivergence
import itertools
from torchmetrics.classification import BinaryAccuracy
from encoder_decoder import Encoder, Decoder, Discriminator
from utils import *


class VAEE(pl.LightningModule):

    def __init__(self,num_features, num_filters, z_dim, args):
        """
        PyTorch Lightning module that summarizes all components to train a VAE.
        Inputs:
            num_features - Number of features in the dataset
            num_filters - Number of channels to use in a CNN encoder/decoder
            z_dim - Dimensionality of latent space
            lr - Learning rate to use for the optimizer
        """
        super().__init__()
        self.args =args
        self.save_hyperparameters()
        self.encoder = Encoder(num_features,num_filters,z_dim)
        self.generator = Encoder(num_features, num_filters,z_dim)
        self.decoder = Decoder(num_features, num_filters,z_dim)
        self.zdim = z_dim
        self.softmax = nn.Softmax()
        self.discriminator = Discriminator(num_features,num_filters,z_dim)
        
        self.loss =  nn.BCELoss()
        self.loss2 = nn.MSELoss()
        self.loss1 = nn.L1Loss()

        self.accuracy = BinaryAccuracy()

        self.lamb = 0.5
        self.automatic_optimization = False
        self.a = 1
        self.b = 1
        self.c = 1
        print('encoder network', self.encoder.net)
        print('decoder network', self.decoder.net)
        print('generator network', self.generator.net)
        print('discriminator network',self.discriminator.net)
        # self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

    def forward(self, x):
        """
        The forward function calculates the VAE-loss for a given batch of images.
        Inputs:
            x - Batch of data [B,C,H].

        Ouptuts:
            reconstruction_loss - The average reconstruction loss of the batch. Shape: single scalar
            regularisation_loss - The average regularization loss (KLD) of the batch. Shape: single scalar
            bpd - The average bits per dimension metric of the batch.
                  This is also the loss we train on. Shape: single scalar
        """

        batch_size = x[0].shape[0]
        mean, log_std = self.encoder(x[0])
        z_samples = sample_reparameterize(mean, torch.exp(log_std)).to(self.device)
        x_hat = self.decoder(z_samples,batch_size)
        
        # x_hat = x_hat.reshape(4,20,13)
        z_hat_mean, z_hat_log_std = self.generator(x_hat)
        z_hat_samples = sample_reparameterize(z_hat_mean, torch.exp(z_hat_log_std)).to(self.device)
        real = self.discriminator(x[0],batch_size)
        fake = self.discriminator(x_hat, batch_size)

        # loss for generator network
        generator_loss = self.loss(self.discriminator(x_hat,batch_size), torch.ones(batch_size, 1, dtype=torch.float32 ))

        # loss for VAE
        reconstruction_loss = self.loss2(x[0],x_hat)
        regularisation_loss = torch.mean(KLD(mean,log_std))

        vae_loss = reconstruction_loss + regularisation_loss

        adversarial_loss = self.loss2(real, fake)

        # encoder loss between the two encoders
        encoder_loss = self.loss1(z_samples, z_hat_samples)
        # loss for discriminator network 
        L_disc_r = self.loss(real,torch.zeros(batch_size, 1, dtype=torch.float32))
        L_disc_f = self.loss(fake,torch.ones(batch_size, 1, dtype=torch.float32 ))

        # complete discriminator loss
        discriminator_loss = (L_disc_r + L_disc_f) * self.lamb

        # accuracy of discriminator
        accuracy_r = self.accuracy(real,torch.zeros(batch_size, 1, dtype=torch.float32))
        accuracy_f = self.accuracy(fake, torch.ones(batch_size, 1, dtype=torch.float32 ))
        accuracy = (accuracy_r + accuracy_f) /2

        # complete generator loss with a,b,c as regularisation terms. Combination of the VAE and AAE loss funtions
        elbo = reconstruction_loss - regularisation_loss.detach()
        vae_loss = encoder_loss * self.a + elbo * self.b + adversarial_loss.detach() * self.c
        bpd = torch.mean(elbo_to_bpd(elbo, x[0].shape))
        return reconstruction_loss, encoder_loss, regularisation_loss, adversarial_loss, discriminator_loss, bpd, vae_loss, accuracy

    @torch.no_grad()
    def sample(self, batch_size):
        """
        Function for sampling a new batch of random images.
        Inputs:
            batch_size - Number of api calls to generate
        Outputs:
            x_samples - Sampled, Shape: [B,C,H]
        """
        z = torch.randn(size=(batch_size,self.zdim)).to(self.device)
        out = self.softmax(self.decoder(z))
        x_samples = torch.multinomial(batch,1)
        return x_samples

    def configure_optimizers(self):
        # Creates the optimizers for the generator network and discriminator network
        optimizer_G = torch.optim.Adam(itertools.chain(self.encoder.parameters(), self.decoder.parameters(), self.generator.parameters()), lr=self.args.lr, betas=(self.args.b1, self.args.b2))
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=self.args.lr, betas=(self.args.b1, self.args.b2))
        return optimizer_G, optimizer_D

    def training_step(self, batch, batch_idx):

        reconstruction_loss, encoder_loss, regularisation_loss, adversarial_loss, discriminator_loss, bpd, vae_loss, accuracy = self.forward(batch)
        torch.autograd.set_detect_anomaly(True)
        optimizer_G, optimizer_D = self.optimizers()
        
        self.toggle_optimizer(optimizer_D)
        self.manual_backward(discriminator_loss,retain_graph=True)
        optimizer_D.step()
        optimizer_D.zero_grad()
        self.untoggle_optimizer(optimizer_D)
        
        self.toggle_optimizer(optimizer_G)
        self.manual_backward(vae_loss,retain_graph=True)
        optimizer_G.step()
        optimizer_G.zero_grad()
        self.untoggle_optimizer(optimizer_G)

        self.log("train_accuracy", accuracy, on_step=False,on_epoch=True)
        self.log("train_reconstruction_loss",reconstruction_loss, on_step=False, on_epoch=True)
        self.log("train_regularization_loss", regularisation_loss, on_step=False, on_epoch=True)
        self.log("train_adversarial_loss", adversarial_loss, on_step=False, on_epoch=True)
        self.log("train_encoder_loss", encoder_loss, on_step=False, on_epoch=True)
        self.log("train_discriminator_loss", discriminator_loss, on_step=False, on_epoch=True)
        self.log("train_VAE_loss", vae_loss, on_step=False, on_epoch=True)

        self.log("train_bpd", bpd, on_step=False, on_epoch=True)

        return bpd

    def validation_step(self, batch, batch_idx):

        L_con, L_enc, L_kl, L_adv, L_disc, bpd, loss, accuracy  = self.forward(batch)

        self.log("validation_accuracy", accuracy, on_step=False,on_epoch=True)
        self.log("validation_reconstruction_loss", L_con, on_step=False, on_epoch=True)
        self.log("validation_regularization_loss", L_kl, on_step=False, on_epoch=True)
        self.log("validation_adversarial_loss", L_adv, on_step=False, on_epoch=True)
        self.log("validation_encoder_loss", L_enc, on_step=False, on_epoch=True)
        self.log("validation_discriminator_loss", L_disc, on_step=False, on_epoch=True)
        self.log('validation_vae_loss', loss, on_step=False, on_epoch=True)
        self.log("val_bpd", bpd, on_step=False, on_epoch=True)

    def test_step(self, batch, batch_idx):

        L_con, L_enc, L_kl, L_adv, L_disc, bpd, loss,accuracy   = self.forward(batch)

        self.log("test_accuracy", accuracy, on_step=False,on_epoch=True)
        self.log("test_reconstruction_loss", L_con, on_step=False, on_epoch=True)
        self.log("test_regularization_loss", L_kl, on_step=False, on_epoch=True)
        self.log("test_adversarial_loss", L_adv, on_step=False, on_epoch=True)
        self.log("test_encoder_loss", L_enc, on_step=False, on_epoch=True)
        self.log("test_discriminator_loss", L_disc, on_step=False, on_epoch=True)
        self.log("test_bpd", bpd, on_step=False, on_epoch=True)

