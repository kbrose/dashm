# -*- coding: utf-8 -*-

import random
import os
from pathlib import Path
from datetime import datetime

import numpy as np

from ..data.load import load
from .make_models import make_models

SAVING_TIME_STRING = '%Y-%m-%d_%H-%M-%S'


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
    now = datetime.utcnow().strftime(SAVING_TIME_STRING) + '_' + str(repo_path)
    save_path = Path(__file__).parent / 'saved' / now
    os.makedirs(save_path, exist_ok=False)

    trainer.save_weights(save_path / 'trainer.h5')
    encoder.save_weights(save_path / 'encoder.h5')
    decoder.save_weights(save_path / 'decoder.h5')


if __name__ == '__main__':
    train('math')
