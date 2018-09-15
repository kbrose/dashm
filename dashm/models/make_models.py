# -*- coding: utf-8 -*-

import os
import io
import contextlib
from typing import Union, Tuple

f = io.StringIO()
with contextlib.redirect_stderr(f):
    from keras.layers import GRU, Input, Dense
    from keras.models import Model

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def make_models(summary : Union[bool, int]=True) -> Tuple[Model, Model, Model]:
    """
    Create the three models necessary for a seq2seq translation
    model, namely a model that can train the weights, a model
    to create an encoding vector from a first sequence, and
    a model that can be repeatedly called to output the translation.

    Inputs
    ------
    summary : True or int > 0
        Whether a summary of the models should be printed to stdout.
        If True, use the line length of 80, otherwise if summary
        is an int > 0, it is used as the line length.

    Returns
    -------
    trainer_model : Model
        A model that can be compiled and fit to train the weights.
    encoder_model : Model
        Model used to create an encoding during inference.
    decoder_model : Model
        Model repeatedly called to create the output during inference.
    """

    hidden_params = {
        'return_sequences': True, 'return_state': False, 'activation': 'relu'
    }
    latent = 32

    # Create the model that will train the weights
    encoder_inp = Input(shape=(None, 128), name='encoder_input')

    def encoder(x):
        x = GRU(8, name='encoder_1', **hidden_params)(x)
        x = GRU(16, name='encoder_2', **hidden_params)(x)
        _, encoder_state = GRU(
            latent, name='encoded', return_sequences=False,
            return_state=True, activation='tanh'
        )(x)
        return encoder_state

    encoder_state = encoder(encoder_inp)

    decoder_inp = Input(shape=(None, 128), name='decoder_input')

    def decoder(x, init_state):
        x = GRU(latent, name='decoder_1', **hidden_params)(
            x, initial_state=init_state
        )
        x = GRU(16, name='decoder_2', **hidden_params)(x)
        outputs, states = GRU(
            latent, name='decoded', return_sequences=True, return_state=True
        )(x)
        return outputs, states

    decoder_outputs, _ = decoder(decoder_inp, encoder_state)

    hidden_layers = [
        Dense(32, activation='relu', name='hidden_1'),
        Dense(64, activation='relu', name='hidden_2'),
        Dense(128, activation='softmax', name='probs')
    ]

    def predictor(x):
        for hl in hidden_layers:
            x = hl(x)
        return x

    preds = predictor(decoder_outputs)

    training_model = Model([encoder_inp, decoder_inp], preds)

    # Create the model used to get encoding vector from input
    encoder_model = Model(encoder_inp, encoder_state)

    # Create the model called repeatedly to build up the output stream
    decoder_state_inp = Input(shape=(latent,), name='decoder_state_input')
    decoder_outputs, decoder_state = decoder(decoder_inp, decoder_state_inp)
    decoder_preds = predictor(decoder_outputs)
    decoder_model = Model([decoder_inp, decoder_state_inp],
                          [decoder_preds, decoder_state])

    if summary:
        line_length = 80 if summary is True else summary
        l = len(' TRAINER MODEL ')
        pad = (line_length - l) // 2
        pad = max(pad, 0)
        print('{0} TRAINER MODEL {0}'.format('#' * pad))
        training_model.summary(line_length=line_length)
        print('{0} ENCODER MODEL {0}'.format('#' * pad))
        encoder_model.summary(line_length=line_length)
        print('{0} DECODER MODEL {0}'.format('#' * pad))
        decoder_model.summary(line_length=line_length)

    return training_model, encoder_model, decoder_model
