# -*- coding: utf-8 -*-

from glob import glob
from pathlib import Path

import numpy as np

"""
Utils to load processed data into python data structures.
"""


def load(repo_path):
    """
    Loads the processed data from
    `<project path>/data/processed-repos/<repo name>` into
    two length-N lists `x,y` of 2D numpy arrays such that

        x[i] : JxL array encoding the commit diff
        y[i] : KxL array encoding the commit message

    The one-hot-encoding is done one character at a time,
    treating the text as ASCII text, and any bytes with
    values > 127 are sent to 127. Thus, `J == 128`.

    Inputs
    ------
    repo : str or Path-like
        A folder within `<project path>/data/processed-repos`

    Returns
    -------
    x,y : two length-N lists of 2D numpy arrays.
    """
    repo_path = Path(__file__).parents[2] / 'data/processed-repos' / repo_path
    commits = set([f.split('.')[0] for f in glob(str(repo_path / '*'))])

    def read_file(f):
        with open(f, 'rb') as fp:
            return fp.read()

    def one_hot_encode_str(s):
        a = np.clip(np.fromstring(s, np.uint8), 0, 127)
        b = np.zeros((a.size, 127), dtype=np.float32)
        b[np.arange(b.shape[0]), a] = 1.0
        return b

    x = [one_hot_encode_str(read_file(c + '.diff')) for c in commits]
    y = [one_hot_encode_str(read_file(c + '.msg')) for c in commits]

    return x, y
