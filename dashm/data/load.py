# -*- coding: utf-8 -*-

from pathlib import Path
import random

import numpy as np
from keras.preprocessing.sequence import pad_sequences

"""
Utils to load processed data into python data structures.
"""

DIFF_END = b'\x01'
MSG_BEGIN = b'\x00'
MSG_END = b'\x01'

__diff_end = np.fromstring(DIFF_END, np.uint8)[0]
__msg_begin = np.fromstring(MSG_BEGIN, np.uint8)[0]
__msg_end = np.fromstring(MSG_END, np.uint8)[0]


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
    x[-1] = __diff_end
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
    x[0] = __msg_begin
    x[-1] = __msg_end
    y = np.zeros((x.size, 128), dtype=np.float32)
    y[np.arange(y.shape[0]), x] = 1.0
    return y


def _read(filename, maxlen=-1):
    with open(filename, 'rb') as fp:
        return fp.read(maxlen)


def load(repo_path, cv_train_split, which, max_diff_len=-1, max_msg_len=-1):
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

        0 : beginning of message
        1 : end of commit message/end of diff

    Data will be split into training/validation by sorting the
    commits SHAs and taking the first section as training and
    the second section as validation.

    WARNING :
        Since data is split by the commit SHAs, data leakage may
        occur. For example, a regular commit and a *merge* commit
        with the same diff/message may be in different splits.

    Inputs
    ------
    repo : str or Path-like
        A folder relative to `<project path>/data/processed-repos`
    cv_train_split : float
        A number between 0 and 1 inclusive, the amount of data
        used for training vs. validation. The number of commits
        multiplied by this number and truncated will be used for
        training and the rest for validation.
    which : str
        One of 'train' or 'val' indicating whether the training
        data or the validation data should be returned respectively.
    max_diff_len : int
        Maximum number of bytes to read from the diff file.
        If negative, the whole file is read. Note that an extra
        byte is added to diffs, so the maximum length of x-data
        returned will be `max_diff_len + 1`.
    max_msg_len : int
        Maximum number of bytes to read from the message file.
        If negative, the whole file is read. Note that an extra
        two bytes are added to messages, so the maximum length of
        y-data returned will be `max_msg_len + 2`.

    Returns
    -------
    (x,y) tuples of lists of 2D numpy arrays.

    See also
    --------
    `one_hot_encode_diff`
    `one_hot_encode_msg`
    """
    repo_path = Path(__file__).parents[2] / 'data/processed-repos' / repo_path
    commits = sorted(set([f.parent / f.stem for f in repo_path.glob('*')]))

    x = [one_hot_encode_diff(_read(c.with_suffix('.diff'), max_diff_len))
         for c in commits]
    y = [one_hot_encode_msg(_read(c.with_suffix('.msg'), max_msg_len))
         for c in commits]

    split = int(len(commits) * cv_train_split)

    if which == 'train':
        return x[:split], y[:split]
    elif which == 'val':
        return x[split:], y[split:]
    else:
        raise ValueError('`which` must be one of ["train", "val"]')


def load_train_generator(repo_path, cv_train_split,
                         max_diff_len=-1, max_msg_len=-1):
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

    The generator will only yield the training portion of the data.

    Inputs
    ------
    repo : str or Path-like
        A folder relative to `<project path>/data/processed-repos`
    cv_train_split : float
        A number between 0 and 1 inclusive, the amount of data
        used for training vs. validation. The number of commits
        multiplied by this number and truncated will be used for
        training and the rest for validation.
    max_diff_len : int
        Maximum number of bytes to read from the diff file.
        If negative, the whole file is read.
    max_msg_len : int
        Maximum number of bytes to read from the message file.
        If negative, the whole file is read.

    WARNING :
        Since data is split by the commit SHAs, data leakage may
        occur. For example, a regular commit and a *merge* commit
        with the same diff/message may be in different splits.

    Returns
    -------
    generator repeatedly yielding
        x,y : Two 2D numpy arrays.
    """
    repo_path = Path(__file__).parents[2] / 'data/processed-repos' / repo_path
    commits = sorted(set([f.parent / f.stem for f in repo_path.glob('*')]))

    split = int(len(commits) * cv_train_split)
    commits = commits[:split]
    while True:
        c = random.choice(commits)
        x = one_hot_encode_diff(_read(c.with_suffix('.diff'), max_diff_len))
        y = one_hot_encode_msg(_read(c.with_suffix('.msg'), max_msg_len))
        yield x, y


def format_batch(batch, max_diff_len, max_msg_len):
    """
    Format a batch by padding sequences with 0s up to the maximum lengths
    given. Also slices the message `y` into `y0` and `y1` similarly to
        y0, y1 = y[:-1], y[1:]
    since the model needs to learn to predict the next element `y1[i]`
    from the current element `y0[i]`.

    Returns values in the format expected by keras for the trainer
    model, i.e. `([x, y0], y1)`, since `x` and `y0` are inputs and `y1`
    is an output.

    Inputs
    ------
    batch : List
        Each element of batch is a tuple of (x,y) data where x is the
        encoded diff and y is the encoded commit message.
    max_diff_len : int
        The encoded diffs will be padded to at most this length by
        adding 0s to the *front* of the sequence. Any encodings
        greater than this length are truncated by removing from
        the *front*. This ensures the end of the diff will still
        be indicated by the special DIFF_END value.
    max_msg_len : int
        The encoded messages will be padded to at most this length by
        adding 0s to the *end* of the sequence. Any encodings
        greater than this length are truncated by removing from
        the *end*. This ensures that the beginning of the message
        is still indicated by the special MSG_BEGIN value.

    Returns
    -------
    ([x,y0], y1)
        x is the 3D padded diff encodings
        y0 is the 3D padded message encodings, except the last element
        y1 is the 3D padded message encodings, except the first element
    """
    xs = [d[0] for d in batch]
    xs = pad_sequences(xs,
                       maxlen=max_diff_len,
                       dtype='float32',
                       padding='pre',
                       truncating='pre',
                       value=0.0)

    ys = [d[1] for d in batch]
    ys = pad_sequences(ys,
                       maxlen=max_msg_len,
                       dtype='float32',
                       padding='post',
                       truncating='post',
                       value=0.0)

    return [xs, ys[:, :-1, :]], ys[:, 1:, :]
