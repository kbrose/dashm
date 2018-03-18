# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil

from dashm.data import get_data


class Test_Clone():
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
        dst = Path(__file__).parents[2] / 'data/raw-repos/dashm-testing'
        assert os.path.exists(dst)
        assert os.path.exists(str(dst) + '.dashm')


class Test_CLI():
    pass
