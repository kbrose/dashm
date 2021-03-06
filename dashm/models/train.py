# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
import argparse
from typing import Union, Tuple

from keras.callbacks import TensorBoard, LambdaCallback
from keras.models import Model

from ..data.load import load_train_generator, load, format_batch
from .make_models import make_models

SAVE_TIME_STRING = '%Y-%m-%d_%H-%M-%S'


def train(repo_path: Union[str, Path], cv_train_split: float,
          summary: bool=False, in_memory: bool=False, **kwargs
          ) -> Tuple[Model, Model, Model]:
    """
    Trains the models against the diff/message data in
    `<project path>/data/processed-repos/<repo_path>`.

    Inputs
    ------
    repo_path : str or Path-like
        Folder in `<project path>/data/processed-repos/` to
        train against.
    cv_train_split : float
        Number between 0 and 1 inclusive. See `data.load.load`.
    summary : bool or int > 0
        Print model summary? passed to make_models()
    **kwargs
        Passed through to model.fit_generator()

    Returns
    -------
    trainer, encoder, decoder : same as make_models()
    """
    # Get the model architectures
    trainer, encoder, decoder = make_models(summary=summary)

    # Compile the model we'll be training
    trainer.compile('adadelta',
                    loss='categorical_crossentropy',
                    metrics=['accuracy'])

    # Get the data ready
    def datagen(batch_size, max_diff_len=200, max_msg_len=200):
        raw_datagen = load_train_generator(repo_path, cv_train_split,
                                           max_diff_len, max_msg_len)
        while True:
            batch = [next(raw_datagen) for _ in range(batch_size)]
            yield format_batch(batch, max_diff_len, max_msg_len)

    val_diff_len = 400
    val_msg_len = 200
    val = load(repo_path, cv_train_split, 'val', max_diff_len=val_diff_len,
               max_msg_len=val_msg_len)
    val = format_batch(list(zip(*val)), val_diff_len, val_msg_len)

    # Prep the output folder
    now = datetime.now().strftime(SAVE_TIME_STRING) + '_' + str(repo_path)
    save_path = Path(__file__).parent / 'saved' / now
    os.makedirs(save_path, exist_ok=False)

    def save_weights(epoch, _):
        try:
            epoch_str = '{:0>3d}'.format(epoch)
        except ValueError:
            epoch_str = epoch
        pairs = [(trainer, 'trainer'), (encoder, 'encoder'),
                 (decoder, 'decoder')]
        for model, name in pairs:
            destination = save_path / (name + '-{}.h5').format(epoch_str)
            model.save_weights(destination)
            symlink_source = (save_path / (name + '.h5'))
            try:
                symlink_source.unlink()
            except FileNotFoundError:
                pass
            symlink_source.symlink_to(destination)

    # Fit the model

    try:
        if in_memory:
            defaults = {
                'batch_size': 64,
                'epochs': 100,
                'callbacks': [TensorBoard(log_dir=str(save_path / 'logs')),
                              LambdaCallback(on_epoch_end=save_weights)]
            }
            defaults.update(kwargs)
            train_data = load(repo_path, cv_train_split, 'train', 200, 200)
            x, y = format_batch(list(zip(*train_data)), 200, 200)
            trainer.fit(x, y, validation_data=val, **defaults)
        else:
            defaults = {
                'steps_per_epoch': 1000,
                'epochs': 100,
                'max_queue_size': 50,
                'workers': 1,
                'callbacks': [TensorBoard(log_dir=str(save_path / 'logs')),
                              LambdaCallback(on_epoch_end=save_weights)]
            }
            defaults.update(kwargs)
            trainer.fit_generator(datagen(64), validation_data=val, **defaults)
    except KeyboardInterrupt:
        save_weights('interrupted', '__unused__')

    return trainer, encoder, decoder


def cli():
    p = argparse.ArgumentParser(
        description='Train a diff -> commit msg translator'
    )
    p.add_argument('repo', type=str,
                   help=('Absolute path to repo, or folder name of a folder'
                         ' that exists in'
                         ' "<project path>/data/processed-repos/".'))
    p.add_argument('cross_validation_split', type=float,
                   help=('Number between 0 and 1 indicating amount of'
                         ' data used for training vs. validation.'))
    p.add_argument('--summary', type=int, default=0,
                   help=('Width in characters of model summary. Use 0 for'
                         ' no summary.'))
    p.add_argument('--steps_per_epoch', type=int, default=1000,
                   help=('Number of training steps per epoch. Only used if'
                         ' --in-memory is not specified.'))
    p.add_argument('--epochs', type=int, default=100,
                   help=('Number of epochs to train for.'))
    p.add_argument('--in-memory', dest='in_memory', action='store_true',
                   help=('Load all data in memory during training.'))

    args = p.parse_args()

    kwargs = {
        'summary': args.summary,
        'epochs': args.epochs,
        'in_memory': args.in_memory
    }
    if not args.in_memory:
        kwargs['steps_per_epoch'] = args.steps_per_epoch
    train(args.repo, args.cross_validation_split, **kwargs)


if __name__ == '__main__':
    cli() # pragma: no cover
