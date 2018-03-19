# -*- coding: utf-8 -*-

from glob import glob
from pathlib import Path

import numpy as np

"""
Utils to load processed data into python data structures.
"""

DIFF_END = b'\x01'
MSG_BEGIN = b'\x00'
MSG_END = b'\x01'


def one_hot_encode_diff(bytes_to_encode):
    """
    One-hot encode the given bytes into 2D float32 numpy array.

    Any bytes with values < 2 are sent to 2, and any values > 127
    are sent to 127. The value1 is used as a special marker:

        1 : end of commit diff

    See also: DIFF_END and MSG_END.

    Inputs
    ------
    bytes_to_encode : bytes
        The bytes to be one-hot encode.

    Returns
    -------
    y : 2D float32 numpy array of one-hot encoded values
    """
    x = np.fromstring(bytes_to_encode + DIFF_END, np.uint8)
    x = np.clip(x, 2, 127)
    y = np.zeros((x.size, 128), dtype=np.float32)
    y[np.arange(y.shape[0]), x] = 1.0
    return y


def one_hot_encode_msg(bytes_to_encode):
    """
    One-hot encode the given bytes into 2D float32 numpy array.

    Any bytes with values < 2 are sent to 2, and any values > 127
    are sent to 127. The values 0 and 1 are used as special markers:

        0 : beginning of commit message
        1 : end of commit message

    See also: DIFF_END and MSG_END.

    Inputs
    ------
    bytes_to_encode : bytes
        The bytes to be one-hot encode.

    Returns
    -------
    y : 2D float32 numpy array of one-hot encoded values
    """
    x = np.fromstring(MSG_BEGIN + bytes_to_encode + MSG_END, np.uint8)
    x = np.clip(x, 2, 127)
    y = np.zeros((x.size, 128), dtype=np.float32)
    y[np.arange(y.shape[0]), x] = 1.0
    return y


def load(repo_path):
    """
    Loads the processed data from
    `<project path>/data/processed-repos/<repo name>` into
    two length-N lists `x,y` of 2D numpy arrays such that

        x[i] : JxL array encoding the commit diff
        y[i] : KxL array encoding the commit message

    The one-hot-encoding is done one character at a time,
    treating the text as ASCII text, and any bytes with
    values < 2 are sent to 2, and any values > 127 are sent
    to 127. The values 0 and 1 are used as special markers:

        0 : end of commit diff
        1 : end of commit message

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

    x = [one_hot_encode_diff(read_file(c + '.diff')) for c in commits]
    y = [one_hot_encode_msg(read_file(c + '.msg')) for c in commits]

    return x, y
