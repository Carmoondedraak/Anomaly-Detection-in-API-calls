gi################################################################################
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
from pytorch_lightning.callbacks import ModelCheckpoint, LearningRateMonitor
import math
from encoder_decoder import Encoder, Decoder, Discriminator
from utils import *
from dataloader_sockshop import sock_data
from vae_discriminator import VAEE


def xavier_init(model):
    for name, param in model.named_parameters():
        if name.endswith(".bias"):
            param.data.fill_(0)
        else:
            if len(param.shape) > 1:
                bound = math.sqrt(6) / math.sqrt(param.shape[0] + param.shape[1])
            else:
                bound = math.sqrt(6) / math.sqrt(param.shape[0])
            param.data.uniform_(-bound, bound)

class GenerateCallback(pl.Callback):

    def __init__(self, batch_size=50, every_n_epochs=5, save_to_disk=False):
        """
        Inputs:
            batch_size - Number of images to generate
            every_n_epochs - Only save those images every N epochs (otherwise tensorboard gets quite large)
            save_to_disk - If True, the samples and image means should be saved to disk as well.
        """
        super().__init__()
        self.batch_size = batch_size
        self.every_n_epochs = every_n_epochs
        self.save_to_disk = save_to_disk

    def on_epoch_end(self, trainer, pl_module):
        """
        This function is called after every epoch.
        Call the save_and_sample function every N epochs.
        """
        if (trainer.current_epoch+1) % self.every_n_epochs == 0:
            self.sample_and_save(trainer, pl_module, trainer.current_epoch+1)

    def sample_and_save(self, trainer, pl_module, epoch):
        """
        Function that generates and save samples from the VAE.
        The generated sample images should be added to TensorBoard and,
        if self.save_to_disk is True, saved inside the logging directory.
        Inputs:
            trainer - The PyTorch Lightning "Trainer" object.
            pl_module - The VAE model that is currently being trained.
            epoch - The epoch number to use for TensorBoard logging and saving of the files.
        """
        samples = pl_module.sample(self.batch_size)
        samples = samples.float() / 15  # Converting 4-bit images to values between 0 and 1
        grid = make_grid(samples, nrow=8, normalize=True, value_range=(0, 1), pad_value=0.5)
        grid = grid.detach().cpu()
        trainer.logger.experiment.add_image("Samples", grid, global_step=epoch)
        if self.save_to_disk:
            save_image(grid,
                        os.path.join(trainer.logger.log_dir, f"epoch_{epoch}_samples.png"))

def train_vae(args):
    """
    Function for training and testing a VAE model.
    Inputs:
        args - Namespace object from the argument parser
    """
    print('epoch', args.epochs)
    os.makedirs(args.log_dir, exist_ok=True)
    train_loader, val_loader, test_loader = sock_data(batch_size=args.batch_size,
                                                   num_workers=args.num_workers,
                                                   root=args.data_dir, names = args.dataset_filenames,abnorm_file = args.abnorm_file,perc=args.perc,real = args.real)


    # Create a PyTorch Lightning trainer with the generation callback
    gen_callback = GenerateCallback(save_to_disk=True)
    save_callback = ModelCheckpoint(save_weights_only=True, mode="min", monitor="val_bpd")
    lr_monitor = LearningRateMonitor(logging_interval='step')

    trainer = pl.Trainer(default_root_dir=args.log_dir,
                         max_epochs=args.epochs,
                         callbacks=[save_callback, gen_callback,lr_monitor],
                         enable_progress_bar=args.progress_bar)
    trainer.logger._default_hp_metric = None  # Optional logging argument that we don't need
    if not args.progress_bar:
        print("[INFO] The progress bar has been suppressed. For updates on the training " + \
              f"progress, check the TensorBoard file at {trainer.logger.log_dir}. If you " + \
              "want to see the progress bar, use the argparse option \"progress_bar\".\n")

    # Create model
    pl.seed_everything(args.seed)  # To be reproducible
    print(args.vaegan)
    model = VAEE(num_features= args.num_features,num_filters=args.num_filters,
                z_dim=args.z_dim,
                args=args)
    xavier_init(model)
    # Training
    # gen_callback.sample_and_save(trainer, model, epoch=0)  # Initial sample
    if args.only_test == False:
        trainer.fit(model, train_loader, val_loader)

    

    # Testing
    # torch.save(model.state_dict(), args.log_dir + args.savefile)
    if args.only_test == True:
        model = VAEE.load_from_checkpoint(args.best_model_checkpoint)
    else:
        model = VAEE.load_from_checkpoint(trainer.checkpoint_callback.best_model_path)
    # with open('my_model.pth', 'rb') as f:
        # buffer = io.BytesIO(f.read())
    # model = torch.load(args.log_dir + args.savefile)
    test_result = trainer.test(model, dataloaders=test_loader, verbose=True)

    # Manifold generation
    if args.z_dim == 2:
        img_grid = visualize_manifold(model.decoder)
        save_image(img_grid,
                   os.path.join(trainer.logger.log_dir, 'vae_manifold.png'),
                   normalize=False)

    return test_result
    



if __name__ == '__main__':
    # Feel free to add more argument parameters
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Model hyperparameters
    parser.add_argument('--z_dim', default=100, type=int,
                        help='Dimensionality of latent space')
    parser.add_argument('--num_filters', default=20, type=int,
                        help='Number of channels/filters to use in the CNN encoder/decoder.')
    
    parser.add_argument('--perc', default=0.5, help='test set anomaly percentage',type=float)

    # Optimizer hyperparameters
    parser.add_argument('--lr', default=1e-3, type=float,
                        help='Learning rate to use')
    
    parser.add_argument('--batch_size', default=128, type=int,
                        help='Minibatch size')
    parser.add_argument('--b1', default=0.5, type=int,help='b1 size')
    parser.add_argument('--b2', default=0.5, type=int, help='b2 size')
    # Other hyperparameters
    parser.add_argument('--data_dir', default='~/Anomaly-Detection-in-API-calls/data', type=str,
                        help='Directory where to look for the data. For jobs on Lisa, this should be $TMPDIR.')
    parser.add_argument('--epochs', default=80, type=int,
                        help='Max number of epochs')
    parser.add_argument('--seed', default=42, type=int,
                        help='Seed to use for reproducing results')
    parser.add_argument('--num_workers', default=4, type=int,
                        help='Number of workers to use in the data loaders. To have a truly deterministic run, this has to be 0. ' + \
                             'For your assignment report, you can use multiple workers (e.g. 4) and do not have to set it to 0.')
    parser.add_argument('--log_dir', default='VAEGANomaly_logs', type=str,
                        help='Directory where the PyTorch Lightning logs should be created.')
    parser.add_argument('--savefile',default='/model.pt')
    parser.add_argument('--progress_bar', action='store_true',
                        help=('Use a progress bar indicator for interactive experimentation. '
                              'Not to be used in conjuction with SLURM jobs'))
    parser.add_argument('--num_features', default=23, help='number of features in the dataset',type=int)
    parser.add_argument('--only_test', default=False, help='train and test or only test')
    parser.add_argument('--best_model_checkpoint', default='/home/cveenker1/VAE_logs/lightning_logs/version_4185017/checkpoints/epoch=0-step=2688.ckpt', help='checkpoint for the trained model')
    # parser.add_argument('--dataset_filenames', default=['train_real.pkl', 'val_real.pkl','test_real.pkl'], help= 'data files for the dataset')
    parser.add_argument('--dataset_filenames', default=['train.pkl', 'val.pkl','test.pkl'], help= 'data files for the dataset',type=str, nargs='*')
    parser.add_argument('--unsupervised', default=True, help='for unsupervised training: True and supervised training: False',action='store_false')
    parser.add_argument('--abnorm_file', default='', help='anomaly test set',type=str)
    parser.add_argument('--real', default=False, help='real data of false data',action='store_true')
    parser.add_argument('--vaegan', default=False, help='use the vaegan architecture instead of vaeganomaly',action='store_true')
    args = parser.parse_args()

    train_vae(args)
# vae best VAE_logs/lightning_logs/version_3956971/checkpoints/epoch=79-step=38720.ckpt
# version_3956971