# -*- coding: utf-8 -*-

from glob import glob
from pathlib import Path

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
            model_dir = max(glob(str(Path(__file__).parent / 'saved' / '*')))

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


if __name__ == '__main__':
    predictor = Predictor()
    s = b'''diff --git a/Makefile b/Makefile
index 9917f99..8a30d76 100644
--- a/Makefile
+++ b/Makefile
@@ -13,6 +13,12 @@ process: raw data/processed-repos/$(human_repo_name).dashm
 data/processed-repos/$(human_repo_name).dashm:
        python -m dashm.data.process_data $(human_repo_name)

+model: data/processed-repos/$(human_repo_name).dashm
+ python -m dashm.models.train $(human_repo_name)
+
+test: clean-code
+ python -m pytest
+
 clean-all: clean-code clean-data

 clean-data: clean-raw clean-processe
'''
    print(predictor.predict(s))
