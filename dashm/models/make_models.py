# -*- coding: utf-8 -*-

import keras


def make_models(summary=True):
    """
    Create the three models necessary for a seq2seq translation
    model, namely a model that can train the weights, a model
    to create an encoding vector from a first sequence, and
    a model that can be repeatedly called to output the translation.

    Inputs
    ------
    summary : True or int > 0
        Whether a summary of the models should be printed to stdout.
        If True, use the default line length, otherwise if summary
        is an int > 0, it is used as the line length.

    Returns
    -------
    trainer_model : keras.models.Model
        A model that can be compiled and fit to train the weights.
    encoder_model : keras.models.Model
        Model used to create an encoding during inference.
    decoder_model : keras.models.Model
        Model repeatedly called to create the output during inference.
    """
    latent_dim = 32

    # Create the model that will train the weights
    encoder_inp = keras.layers.Input(shape=(None, 128), name='encoder_input')
    encoder = keras.layers.GRU(latent_dim, return_state=True, name='encoder')
    _, encoder_state = encoder(encoder_inp)

    decoder_inp = keras.layers.Input(shape=(None, 128), name='decoder_input')
    decoder = keras.layers.GRU(latent_dim, return_sequences=True,
                               return_state=True, name='decoder')
    decoder_outputs, _ = decoder(decoder_inp, initial_state=encoder_state)

    predictor = keras.layers.Dense(128, activation='softmax', name='probs')
    preds = predictor(decoder_outputs)

    training_model = keras.models.Model([encoder_inp, decoder_inp], preds)

    # Create the model used to get encoding vector from input
    encoder_model = keras.models.Model(encoder_inp, encoder_state)

    # Create the model called repeatedly to build up the output stream
    decoder_state_inp = keras.layers.Input(shape=(latent_dim,),
                                           name='decoder_state_input')
    decoder_outputs, decoder_state = decoder(decoder_inp,
                                             initial_state=decoder_state_inp)
    decoder_preds = predictor(decoder_outputs)
    decoder_model = keras.models.Model([decoder_inp, decoder_state_inp],
                                       [decoder_preds, decoder_state])

    if summary:
        line_length = 80 if summary is True else summary
        print('{0} TRAINER MODEL {0}'.format('#'*15))
        training_model.summary(line_length=line_length)
        print('{0} ENCODER MODEL {0}'.format('#'*15))
        encoder_model.summary(line_length=line_length)
        print('{0} DECODER MODEL {0}'.format('#'*15))
        decoder_model.summary(line_length=line_length)

    return training_model, encoder_model, decoder_model
