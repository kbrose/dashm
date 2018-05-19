# -*- coding: utf-8 -*-

from pathlib import Path
import sys
import unicodedata

import numpy as np

from .make_models import make_models
from ..data.load import one_hot_encode_diff, one_hot_encode_msg, MSG_END


def load_models(model_dir):
    trainer, encoder, decoder = make_models(summary=False)

    trainer.load_weights(Path(model_dir) / 'trainer.h5')
    encoder.load_weights(Path(model_dir) / 'encoder.h5')
    decoder.load_weights(Path(model_dir) / 'decoder.h5')

    return trainer, encoder, decoder


class Predictor():
    """
    Make predictions using a model saved to disk.
    """

    def __init__(self, model_dir=None):
        """
        Inputs
        ------
        model_dir : str or Path-like
            Path to the folder containing the saved model, relative
            to `<project path>/models/saved/`. Should contain files
            "trainer.h5", "encoder.h5", and "decoder.h5".
            DEFAULT: None, takes the most recent model.

        See also
        --------
            `load_models`
        """
        if model_dir is None:
            model_dir = '*'
        model_dir = str(model_dir)
        model_dirs = list((Path(__file__).parent / 'saved').glob(model_dir))
        if not model_dirs:
            raise RuntimeError('No saved models found.')
        model_dir = max(model_dirs)

        _, encoder, decoder = load_models(model_dir)
        self.encoder = encoder
        self.decoder = decoder

        self._init_probs = np.expand_dims(one_hot_encode_msg(b'')[0:1], 0)

    def state_from_diff(self, diff):
        """
        Get the state encoded from the given diff.

        Inputs
        ------
        diff : str or bytes-like
            The git-diff to encode into a state passed to the decoder.
        """
        try:
            diff = unicodedata.normalize('NFKD', diff)
            diff = diff.encode('ascii', 'ignore')
        except TypeError:
            # diff already given in bytes
            pass

        x = np.expand_dims(one_hot_encode_diff(diff), 0)
        return self.encoder.predict(x)

    def _proba_generator(self, state):
        """
        Generator to output probabilities.
        """
        probs = self._init_probs
        while True:
            probs, state = self.decoder.predict([probs, state])
            yield probs

    def predict_proba(self, diff, n=300):
        """
        Predicts a sequence of `n` of the commit message for a given
        diff. Outputs a probability distribution over the possible
        characters at each step.

        Inputs
        ------
        diff : str or bytes-like
            The git-diff that we will try to summarize into a message.
        n : int
            Number of steps to predict.

        Returns
        -------
        out_probs : numpy.ndarray
            (n, num_characters)-shaped array
        """
        state = self.state_from_diff(diff)
        gen = self._proba_generator(state)
        out_probs = np.array([next(gen) for i in range(n)])

        return out_probs

    def predict(self, diff, max_len=300):
        """
        Predict the commit message for the given diff. Cut the
        message off if it grows too long.

        Inputs
        ------
        diff : str or bytes-like
            The git-diff that we will try to summarize into a message.
        max_len : int
            Cut the message off if we get this many characters
            without seeing the `dashm.data.load.MSG_END` character.
        """
        state = self.state_from_diff(diff)
        gen = self._proba_generator(state)
        out = []
        while max_len > 0:
            probs = next(gen)
            out.append(chr(probs.argmax()).encode('ascii'))
            if out[-1] == MSG_END:
                break
            max_len -= 1
        return b''.join(out[1:-1]) # 1:-1 to cut out MSG_BEGIN/MSG_END


def cli():
    predictor = Predictor()
    s = sys.stdin.read()
    print(predictor.predict(s).decode('ascii'))


if __name__ == '__main__':
    cli() # pragma: no cover
