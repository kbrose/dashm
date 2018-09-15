# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
import shutil

from dashm.data import get_data


class Test_Clone():
    @classmethod
    def _clean(cls):
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

    @classmethod
    def setup_method(cls):
        cls.__old_sys_argv = sys.argv
        cls._clean()

    @classmethod
    def teardown_method(cls):
        cls._clean()
        sys.argv = cls.__old_sys_argv

    def assert_cloned_correctly(self):
        dst = Path(__file__).parents[2] / 'data/raw-repos/dashm-testing'
        assert dst.exists()
        assert dst.with_suffix('.dashm').exists()

    def test_clone(self):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')
        self.assert_cloned_correctly()

    def test_cli(self):
        sys.argv = ['python', 'https://github.com/kbrose/dashm-testing.git']
        get_data.cli()
        self.assert_cloned_correctly()
