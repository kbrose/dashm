# -*- coding: utf-8 -*-

import random
import os
from pathlib import Path
from datetime import datetime
import argparse

import numpy as np

from ..data.load import load
from .make_models import make_models

SAVE_TIME_STRING = '%Y-%m-%d_%H-%M-%S'


def train(repo_path, summary=False, **kwargs):
    """
    Trains the models against the diff/message data in
    `<project path>/data/processed-repos/<repo_path>`.

    Inputs
    ------
    repo_path : str or Path-like
        Folder in `<project path>/data/processed-repos/` to
        train against.
    summary : bool or int > 0
        Print model summary? passed to make_models()
    **kwargs
        Passed through to model.fit_generator()
    """
    # Get the model architectures
    trainer, encoder, decoder = make_models(summary=summary)

    # Compile the model we'll be training
    trainer.compile('adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])

    # Get the data ready
    x, y = load(repo_path)

    def datagen(max_diff_len=200):
        index_choices = range(len(x))
        while True:
            i = random.choice(index_choices)
            ix = np.expand_dims(x[i], 0)
            iy = np.expand_dims(y[i], 0)
            if ix.shape[1] > max_diff_len:
                j = np.random.randint(ix.shape[1] - max_diff_len)
                ix = ix[:, j:j+max_diff_len, :]
            yield [ix, iy[:, :-1, :]], iy[:, 1:, :]

    # Fit the model
    defaults = {'steps_per_epoch': 1000, 'epochs': 100}
    defaults.update(kwargs)
    trainer.fit_generator(datagen(), **defaults)

    # Save the models
    now = datetime.utcnow().strftime(SAVE_TIME_STRING) + '_' + str(repo_path)
    save_path = Path(__file__).parent / 'saved' / now
    os.makedirs(save_path, exist_ok=False)

    trainer.save_weights(save_path / 'trainer.h5')
    encoder.save_weights(save_path / 'encoder.h5')
    decoder.save_weights(save_path / 'decoder.h5')


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description='Train a diff -> commit msg translator'
    )
    p.add_argument('repo', type=str,
                   help=('Absolute path to repo, or folder name of a folder'
                         ' that exists in'
                         ' "<project path>/data/processed-repos/".'))
    p.add_argument('--summary', type=int, default=0,
                   help=('Width in characters of model summary. Use 0 for'
                         ' no summary.'))
    p.add_argument('--steps_per_epoch', type=int, default=100,
                   help=('Number of training steps per epoch.'))
    p.add_argument('--epochs', type=int, default=10,
                   help=('Number of training steps per epoch.'))

    args = p.parse_args()

    train(args.repo,
          summary=args.summary,
          steps_per_epoch=args.steps_per_epoch,
          epochs=args.epochs)
