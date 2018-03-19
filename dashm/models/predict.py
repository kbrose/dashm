# -*- coding: utf-8 -*-

from glob import glob
from pathlib import Path
import sys

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
    TODO
    """
    def __init__(self, model_dir=None):
        """
        TODO
        """
        if model_dir is None:
            model_dir = '*'
        model_dirs = glob(str(Path(__file__).parent / 'saved' / model_dir))
        if not model_dirs:
            raise RuntimeError('No saved models found.')
        model_dir = max(model_dirs)

        _, encoder, decoder = load_models(model_dir)
        self.encoder = encoder
        self.decoder = decoder

    def predict_proba(self, diff, max_len=300):
        """
        TODO
        """
        try:
            diff = diff.encode('ascii')
        except AttributeError:
            pass

        x = np.expand_dims(one_hot_encode_diff(diff), 0)

        state = self.encoder.predict(x)
        out_probs = [np.expand_dims(one_hot_encode_msg(b'')[0:1], 0)]
        for _ in range(max_len):
            # y = np.expand_dims(one_hot_encode_msg(out[-1])[1:2], 0)
            preds, state = self.decoder.predict([out_probs[-1], state])
            out_probs.append(preds)
            if chr(np.argmax(preds[0])).encode('ascii') == MSG_END:
                break

        return out_probs

    def predict(self, diff, max_len=300):
        """
        TODO
        """
        probs = self.predict_proba(diff, max_len)
        return b''.join([chr(np.argmax(y)).encode('ascii') for y in probs])


def cli():
    predictor = Predictor()
    s = sys.stdin.read()
    print(predictor.predict(s).decode('ascii'))


if __name__ == '__main__':
    cli()
