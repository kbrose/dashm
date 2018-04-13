# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
import argparse

from keras.preprocessing.sequence import pad_sequences
from keras.callbacks import TensorBoard

from ..data.load import load_generator
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
    trainer.compile('adadelta',
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])

    # Get the data ready
    def datagen(batch_size, max_diff_len=200, max_msg_len=200):
        raw_datagen = load_generator(repo_path, max_diff_len, max_msg_len)
        while True:
            data = [next(raw_datagen) for _ in range(batch_size)]

            xs = [d[0] for d in data]
            xs = pad_sequences(xs,
                               maxlen=max_diff_len,
                               dtype='float32',
                               padding='pre',
                               truncating='post',
                               value=0.0)

            ys = [d[1] for d in data]
            ys = pad_sequences(ys,
                               maxlen=max_msg_len,
                               dtype='float32',
                               padding='pre',
                               truncating='post',
                               value=0.0)

            yield [xs, ys[:, :-1, :]], ys[:, 1:, :]

    # Prep the output folder
    now = datetime.now().strftime(SAVE_TIME_STRING) + '_' + str(repo_path)
    save_path = Path(__file__).parent / 'saved' / now
    os.makedirs(save_path, exist_ok=False)

    # Fit the model
    defaults = {'steps_per_epoch': 1000,
                'epochs': 100,
                'max_queue_size': 50,
                'workers': 1,
                'callbacks': [TensorBoard(log_dir=str(save_path / 'logs'))]}
    defaults.update(kwargs)
    trainer.fit_generator(datagen(64), **defaults)

    # Save the models
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
    p.add_argument('--steps_per_epoch', type=int, default=1000,
                   help=('Number of training steps per epoch.'))
    p.add_argument('--epochs', type=int, default=100,
                   help=('Number of training steps per epoch.'))

    args = p.parse_args()

    train(args.repo,
          summary=args.summary,
          steps_per_epoch=args.steps_per_epoch,
          epochs=args.epochs)
