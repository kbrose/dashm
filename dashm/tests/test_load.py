# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil

import pytest

from dashm.data import get_data
from dashm.data import process_data
from dashm.data import load

class Test_Load():
    @classmethod
    def setup_class(cls):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')
        process_data.process('dashm-testing')

    @classmethod
    def teardown_class(cls):
        cls.data_path = Path(__file__).parents[2] / 'data/'
        for interim in ['raw-repos', 'processed-repos']:
            dst = cls.data_path / interim / 'dashm-testing'
            try:
                shutil.rmtree(dst)
            except FileNotFoundError:
                pass
            try:
                os.remove(str(dst) + '.dashm')
            except FileNotFoundError:
                pass

    @staticmethod
    def test_load():
        x_train, y_train = load.load('dashm-testing', 0.5, 'train')
        assert len(x_train) == len(y_train)
        for x, y in zip(x_train, y_train):
            assert (x.sum(axis=1) == 1).all()
            assert (y.sum(axis=1) == 1).all()

        x_val, y_val = load.load('dashm-testing', 0.5, 'val')
        assert len(x_val) == len(y_val)
        for x, y in zip(x_val, y_val):
            assert (x.sum(axis=1) == 1).all()
            assert (y.sum(axis=1) == 1).all()

        assert abs(len(x_val) - len(x_train)) <= 1
        assert abs(len(y_val) - len(y_train)) <= 1

    @staticmethod
    def test_load_bad_which():
        with pytest.raises(ValueError):
            load.load('dashm-testing', 0.5, 'non-existent')

    @staticmethod
    def test_load_max_diff_len():
        x_train, y_train = load.load('dashm-testing', 1.0, 'train')
        # if some len isn't > 1 originally then this doesn't test anything.
        assert any(len(x) > 2 for x in x_train)

        # One extra byte is added to diff messages, so a max_diff_len
        # of 1 will result in at most 2-length x values.
        x_train2, y_train2 = load.load('dashm-testing', 1.0, 'train',
                                       max_diff_len=1)
        assert all(len(x) <= 2 for x in x_train2)

        # make sure max_diff_len didn't effect messages
        for y, y2 in zip(y_train, y_train2):
            assert y.shape == y2.shape
            assert (y.flatten() == y2.flatten()).all()

    @staticmethod
    def test_load_max_msg_len():
        x_train, y_train = load.load('dashm-testing', 1.0, 'train')
        # if some len isn't > 1 originally then this doesn't test anything.
        assert any(len(y) > 3 for y in y_train)

        # Two extra bytes are added to diff messages, so a max_msg_len
        # of 1 will result in at most 3-length x values.
        x_train2, y_train2 = load.load('dashm-testing', 1.0, 'train',
                                       max_msg_len=1)
        assert all(len(y) <= 3 for y in y_train2)

        # make sure max_msg_len didn't effect diffs
        for x, x2 in zip(x_train, x_train2):
            assert x.shape == x2.shape
            assert (x.flatten() == x2.flatten()).all()

    @staticmethod
    def test_load_generator():
        g = load.load_train_generator('dashm-testing', 0.5)
        x, y = next(g)
        assert (x.sum(axis=1) == 1).all()
        assert (y.sum(axis=1) == 1).all()

    @staticmethod
    def test_format_batch():
        g = load.load_train_generator('dashm-testing', 0.5)
        batch_len = 10
        batch = [next(g) for _ in range(batch_len)]

        batch = load.format_batch(batch, 400, 200)

        assert batch[0][0].shape[0] == batch_len
        assert batch[0][1].shape[0] == batch_len
        assert batch[1].shape[0] == batch_len


class Test_CLI():
    pass
