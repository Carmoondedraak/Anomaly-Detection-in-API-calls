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
from torchmetrics.classification import BinaryAccuracy, BinaryRecall, BinaryPrecision, BinaryConfusionMatrix
from encoder_decoder import Encoder, Decoder, Discriminator
from utils import *
from torch.optim.lr_scheduler import  ReduceLROnPlateau 
import matplotlib.pyplot as plt


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
        # print('number of features',num_features)
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
        self.precision = BinaryPrecision()
        self.recall = BinaryRecall()
        self.CM = BinaryConfusionMatrix()

        self.B = 0.5
        self.lamb = 0.5
        self.automatic_optimization = False
        self.a = 1
        self.b = 1
        self.c = 1
        self.unsupervised = args.unsupervised
        self.vaegan = args.vaegan
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
        # print('the shape',x[0].shape )
        mean, log_std = self.encoder(x[0])
        z_samples = sample_reparameterize(mean, torch.exp(log_std)).to(self.device)
        x_hat = self.decoder(z_samples,batch_size)
        
        z_hat_mean, z_hat_log_std = self.generator(x_hat)
        z_hat_samples = sample_reparameterize(z_hat_mean, torch.exp(z_hat_log_std)).to(self.device)
        real, output_r = self.discriminator(x[0],batch_size)
        fake, output_f = self.discriminator(x_hat, batch_size)

        return x_hat, z_samples,z_hat_samples, real,fake, mean, log_std,output_r,output_f

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
        scheduler_g = ReduceLROnPlateau(optimizer_G,'min')
        optimizer_D = torch.optim.Adam(self.discriminator.parameters(), lr=self.args.lr, betas=(self.args.b1, self.args.b2))
        scheduler_d = ReduceLROnPlateau(optimizer_D, 'min')

        return [{'optimizer':optimizer_D,'lr_scheduler':{'scheduler': scheduler_d, 'monitor':'validation_loss_total'}},{'optimizer':optimizer_G,'lr_scheduler':{'scheduler':scheduler_g,'monitor':'validation_total_loss'}}]

    def training_step(self, batch, batch_idx):
        # forwards pass
        # print('label', batch[1])
        batch_size = batch[0].shape[0]
        x_hat, z_samples, z_hat_samples, real,fake, mean, log_std,output_r,output_f = self.forward(batch)
        preds = torch.cat((real,fake))
        labels = torch.cat((torch.zeros(batch_size, 1, dtype=torch.float32),torch.ones(batch_size, 1, dtype=torch.float32)))

        # loss for generator network/VAE
        reconstruction_loss = self.loss2(batch[0],x_hat)
        regularisation_loss = torch.mean(KLD(mean,log_std))
        adversarial_loss = self.loss1(output_r,output_f)

        # discriminator loss
        discriminator_loss = self.loss(preds,labels)

        # complete generator loss with a,b,c as regularisation terms. Combination of the VAE and AAE loss funtions
        elbo = reconstruction_loss + regularisation_loss.detach()
        
        if self.vaegan == True:
            loss = elbo * self.b + adversarial_loss.detach() * self.c
        else:
            # encoder loss between the two encoders
            encoder_loss = self.loss1(z_samples, z_hat_samples)
            loss = encoder_loss * self.a + elbo * self.b + adversarial_loss.detach() * self.c


        bpd = torch.mean(elbo_to_bpd(elbo, batch[0].shape))

        # metrics
        accuracy = self.accuracy(preds, labels)
        precision = self.precision(preds,labels)
        recall = self.recall(preds, labels)
        cm = self.CM(preds,labels)
        tn = cm[0][0]
        fn = cm[1][0]
        tp = cm[1][1]
        fp = cm[0][1]
        ppv = (tp * self.B)/ (tp *self.B + fp *(1-self.B))

        # backwards pass
        torch.autograd.set_detect_anomaly(True)
        optimizers = self.optimizers()
        schedulers = self.lr_schedulers()
        self.toggle_optimizer(optimizers[0])
        self.manual_backward(discriminator_loss,retain_graph=True)
        optimizers[0].step()
        optimizers[0].zero_grad()
        self.untoggle_optimizer(optimizers[0])
        
        self.toggle_optimizer(optimizers[1])
        self.manual_backward(loss,retain_graph=True)
        optimizers[1].step()
        optimizers[1].zero_grad()
        self.untoggle_optimizer(optimizers[1])

        # schedulers[0].step(self.val_loss)
        # schedulers[0].step()
        # schedulers[1].step(self.val_loss)
        # logging
        self.visualise_latent(z_samples)
        self.visualise_convolutions()
        if self.vaegan == False:
            self.log("train_encoder_loss", encoder_loss, on_step=False, on_epoch=True)

        self.log("train_accuracy", accuracy, on_step=True,on_epoch=True)
        self.log("train_reconstruction_loss",reconstruction_loss, on_step=False, on_epoch=True)
        self.log("train_regularization_loss", regularisation_loss, on_step=False, on_epoch=True)
        self.log("train_adversarial_loss", adversarial_loss, on_step=False, on_epoch=True)
        self.log("train_discriminator_loss", discriminator_loss, on_step=False, on_epoch=True)
        self.log("train_total_loss", loss, on_step=False, on_epoch=True)
        self.log("train_bpd", bpd, on_step=False, on_epoch=True)
        self.log("train_precision", precision, on_step=False, on_epoch=True)
        self.log("train_recall", recall, on_step=False, on_epoch=True)
        self.log("train_ppv", ppv, on_step=False,on_epoch=True)

        return bpd

    def validation_step(self, batch, batch_idx):
        # forwards pass
        batch_size = batch[0].shape[0]
        x_hat, z_samples,z_hat_samples, real,fake, mean, log_std,output_r,output_f = self.forward(batch)
        preds = torch.cat((real,fake))
        labels = torch.cat((torch.zeros(batch_size, 1, dtype=torch.float32),torch.ones(batch_size, 1, dtype=torch.float32)))
        
        # loss for generator network/VAE
        # generator_loss = self.loss(self.discriminator(x_hat,batch_size), torch.ones(batch_size, 1, dtype=torch.float32 ))
        L_con = self.loss2(batch[0],x_hat)
        L_kl = torch.mean(KLD(mean,log_std))
        L_adv = self.loss1(output_r,output_f)

        # complete discriminator loss
        L_disc = (self.loss(preds,labels))


        # complete generator loss with a,b,c as regularisation terms. Combination of the VAE and AAE loss funtions
        elbo = - L_con + L_kl.detach()
        if self.vaegan == True:
            loss = elbo * self.b + L_adv.detach() * self.c
        else:
            # encoder loss between the two encoders
            L_enc = self.loss1(z_samples, z_hat_samples)
            loss = L_enc * self.a + elbo * self.b + L_adv.detach() * self.c

        


        # metrics
        accuracy = self.accuracy(preds, labels)
        precision = self.precision(preds,labels)
        recall = self.recall(preds, labels)
        cm = self.CM(preds,labels)
        tn = cm[0][0]
        fn = cm[1][0]
        tp = cm[1][1]
        fp = cm[0][1]
        ppv = (tp * self.B)/ (tp *self.B + fp *(1-self.B))

        bpd = torch.mean(elbo_to_bpd(elbo, batch[0].shape))
        self.val_loss = loss
        # logging
        if self.vaegan == False:
            self.log("validation_encoder_loss", L_enc, on_step=False, on_epoch=True)
            
        self.log("validation_accuracy", accuracy, on_step=True,on_epoch=True)
        self.log("validation_precision", precision,on_step=True,on_epoch=True)
        self.log("validation_recall",recall, on_step=False, on_epoch=True)
        self.log("validation_ppv", ppv, on_step=False, on_epoch=True)
        self.log("validation_reconstruction_loss", L_con, on_step=False, on_epoch=True)
        self.log("validation_regularization_loss", L_kl, on_step=False, on_epoch=True)
        self.log("validation_adversarial_loss", L_adv, on_step=False, on_epoch=True)
        self.log("validation_discriminator_loss", L_disc, on_step=False, on_epoch=True)
        self.log('validation_total_loss', loss, on_step=False, on_epoch=True)
        self.log("val_bpd", bpd, on_step=False, on_epoch=True)

    def test_step(self, batch, batch_idx):
        # forwards pass
        batch_size = batch[0].shape[0]
        x_hat, z_samples,z_hat_samples, real,fake, mean, log_std,output_r,output_f = self.forward(batch)

        # loss for generator network
        batch[1] = batch[1].reshape(batch_size,1)
        # generator_loss = self.loss(self.discriminator(batch[0],batch_size),batch[1])

        if self.unsupervised == False:
            print('hierr')
            preds = real
            labels = batch[1]

        else: 
            preds = torch.cat((real,fake))
            labels = torch.cat((torch.zeros(batch_size, 1, dtype=torch.float32),torch.ones(batch_size, 1, dtype=torch.float32)))
        # loss for VAE
        
        L_con = self.loss2(batch[0],x_hat)
        L_kl = torch.mean(KLD(mean,log_std))
        L_adv = self.loss1(output_r,output_f)
        
        # loss for discriminator network 
        L_disc = self.loss(preds,labels)

        # complete generator loss with a,b,c as regularisation terms. Combination of the VAE and AAE loss funtions
        elbo = - L_con + L_kl
        if self.vaegan == True:
            loss = elbo * self.b + L_adv.detach() * self.c
        else:
            # encoder loss between the two encoders
            L_enc = self.loss1(z_samples, z_hat_samples)
            loss = L_enc * self.a + elbo * self.b + L_adv * self.c

        # metrics
        accuracy = self.accuracy(preds,labels)
        precision = self.precision(preds,labels)
        recall = self.recall(preds,labels)
        cm = self.CM(preds,labels)
        tn = cm[0][0]
        fn = cm[1][0]
        tp = cm[1][1]
        fp = cm[0][1]
        ppv = (tp * self.B)/ (tp *self.B + fp *(1-self.B))

        bpd = torch.mean(elbo_to_bpd(elbo, batch[0].shape))
        
        # logging
        if self.vaegan == False:
            self.log("test_encoder_loss", L_enc, on_step=False, on_epoch=True)

        self.log("test_total_loss",loss, on_step=False, on_epoch=True)
        self.log("test_accuracy", accuracy, on_step=False,on_epoch=True)
        self.log("test_precision", precision,on_step=False,on_epoch=True)
        self.log("test_recall",recall, on_step=False, on_epoch=True)
        self.log("test_ppv", ppv, on_step=False, on_epoch=True)
        self.log("test_reconstruction_loss", L_con, on_step=False, on_epoch=True)
        self.log("test_regularization_loss", L_kl, on_step=False, on_epoch=True)
        self.log("test_adversarial_loss", L_adv, on_step=False, on_epoch=True)
        self.log("test_discriminator_loss", L_disc, on_step=False, on_epoch=True)
        self.log("test_bpd", bpd, on_step=False, on_epoch=True)

    def visualise_latent(self,latent_representations):
        fig = plt.figure(figsize=(10,8))

        plt.scatter(range(latent_representations.shape[0]* latent_representations.shape[1]), latent_representations.detach().numpy(), c='b', marker='o', label='Latent Space')
        plt.xlabel('Data Points')
        plt.ylabel('Latent Representations')
        plt.legend()
        plt.title('1D VAE Latent Space')
        plt.clf()

        tensorboard = self.logger.experiment
        tensorboard.add_figure('latent_space',fig,self.global_step)
        tensorboard.add_histogram('latent_space_hist',latent_representations,self.global_step)

    def visualise_convolutions(self):
        tensorboard = self.logger.experiment
        # for i in range(len(self.encoder.net)):
        for i,name in enumerate(self.encoder.net.named_children()):
            if 'Conv1d' in str(name[1]):
                im = self.encoder.net[i].weight.data.detach().numpy()
                if im.shape[1] == 1:
                        im = im.reshape(im.shape[1],im.shape[0],im.shape[2])
                        print(im.shape)
                        tensorboard.add_image('encoder_network_activation_{}'.format(i),im,self.global_step)
                else:
                    for j in range(im.shape[2]):
                            im = im[:,:,j]
                            im = im.reshape(1,im.shape[0],im.shape[1])
    
                            tensorboard.add_image('encoder_network_activation_{}_{}'.format(i,j),im,self.global_step)

                # tensorboard.add_image('encoder_network_convolution_{}'.format(i),im,self.global_step)
            activation = self.encoder.net[1]
            # if 'LeakyReLU' in str(name[1]):
                # im = self.encoder.net[i].weight.data.detach().numpy()
                # tensorboard.add_image('encoder_network_activation_{}'.format(i),im,self.global_step)

        print('hallo')
        # for name, module in self.decoder.net.named_children():
        #     print(name,module)
        # for name,module in self.discriminator.net.named_children():
        #     print(name,module)
        # for name, module in self.generator.net.named_children():
        #     print(name,module)
    # def supervised_forward(self, x):
    #     """
    #     The forward function calculates the VAE-loss for a given batch of images.
    #     Inputs:
    #         x - Batch of data [B,C,H].

    #     Ouptuts:
    #         reconstruction_loss - The average reconstruction loss of the batch. Shape: single scalar
    #         regularisation_loss - The average regularization loss (KLD) of the batch. Shape: single scalar
    #         bpd - The average bits per dimension metric of the batch.
    #               This is also the loss we train on. Shape: single scalar
    #     """
    #     print('the targets', x[1])
    #     batch_size = x[0].shape[0]
    #     mean, log_std = self.encoder(x[0])
    #     z_samples = sample_reparameterize(mean, torch.exp(log_std)).to(self.device)
    #     x_hat = self.decoder(z_samples,batch_size)
        
    #     # x_hat = x_hat.reshape(4,20,13)
    #     z_hat_mean, z_hat_log_std = self.generator(x_hat)
    #     z_hat_samples = sample_reparameterize(z_hat_mean, torch.exp(z_hat_log_std)).to(self.device)
    #     real = self.discriminator(x[0],batch_size)

        
    #     return reconstruction_loss, encoder_loss, regularisation_loss, adversarial_loss, discriminator_loss, bpd, vae_loss, accuracy

  