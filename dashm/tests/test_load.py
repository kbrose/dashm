# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil

from dashm.data import get_data
from dashm.data import process_data
from dashm.data import load

class Test_Process():
    @classmethod
    def setup_method(cls):
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

    teardown_method = setup_method

    def test_clone(self):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')
        process_data.process('dashm-testing')

        x,y = load.load('dashm-testing')

        assert len(x) == len(y)

        for ix, iy in zip(x,y):
            assert (ix.sum(axis=1) == 1).all()
            assert (iy.sum(axis=1) == 1).all()

class Test_CLI():
    pass
