# -*- coding: utf-8 -*-

from glob import glob
from pathlib import Path
import random

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
    are sent to 127. The value 1 is used as a special marker:

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
    x[-1] = np.fromstring(DIFF_END, np.uint8)[0]
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
    x[0] = np.fromstring(MSG_BEGIN, np.uint8)[0]
    x[-1] = np.fromstring(MSG_END, np.uint8)[0]
    y = np.zeros((x.size, 128), dtype=np.float32)
    y[np.arange(y.shape[0]), x] = 1.0
    return y


def _read_file(filename, maxlen=-1):
    with open(filename, 'rb') as fp:
        return fp.read(maxlen)


def load(repo_path, max_diff_len=-1, max_msg_len=-1):
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
    max_diff_len : int
        Maximum number of bytes to read from the diff file.
        If negative, the whole file is read.
    max_msg_len : int
        Maximum number of bytes to read from the message file.
        If negative, the whole file is read.

    Returns
    -------
    x,y : two length-N lists of 2D numpy arrays.
    """
    repo_path = Path(__file__).parents[2] / 'data/processed-repos' / repo_path
    commits = set([f.split('.')[0] for f in glob(str(repo_path / '*'))])

    x = [one_hot_encode_diff(_read_file(c + '.diff', max_diff_len))
         for c in commits]
    y = [one_hot_encode_msg(_read_file(c + '.msg', max_msg_len))
         for c in commits]

    return x, y


def load_generator(repo_path, max_diff_len=-1, max_msg_len=-1):
    """
    A generator giving access to the data located in
    `<project path>/data/processed-repos/<repo name>`.
    Will continue to return samples x,y with

        x : JxL array encoding the commit diff
        y : KxL array encoding the commit message

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
    max_diff_len : int
        Maximum number of bytes to read from the diff file.
        If negative, the whole file is read.
    max_msg_len : int
        Maximum number of bytes to read from the message file.
        If negative, the whole file is read.

    Returns
    -------
    generator repeatedly yielding
        x,y : Two 2D numpy arrays.
    """
    repo_path = Path(__file__).parents[2] / 'data/processed-repos' / repo_path
    commits = list(set([f.split('.')[0] for f in glob(str(repo_path / '*'))]))

    while True:
        c = random.choice(commits)
        x = one_hot_encode_diff(_read_file(c + '.diff', max_diff_len))
        y = one_hot_encode_msg(_read_file(c + '.msg', max_msg_len))
        yield x, y
