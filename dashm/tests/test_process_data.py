# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil
from glob import glob
import sys

from dashm.data import get_data
from dashm.data import process_data

class Test_Process():
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

    def assert_processed_correctly(self):
        dst = self.data_path / 'processed-repos/dashm-testing'
        assert os.path.exists(dst)
        assert os.path.exists(str(dst) + '.dashm')

        expected_files = Path(__file__).parent / 'data/dashm-testing/*'
        actual_files = [os.path.split(x)[-1] for x in glob(str(dst / '*'))]
        for f in glob(str(expected_files)):
            assert os.path.split(f)[-1] in actual_files
            with open(f) as fp:
                expected_contents = fp.read()
            with open(dst / os.path.split(f)[-1]) as fp:
                actual_contents = fp.read()
            assert expected_contents == actual_contents

    def test_process(self):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')

        process_data.process('dashm-testing')
        self.assert_processed_correctly()

    def test_cli_folder_name(self):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')

        sys.argv = ['python', 'dashm-testing']

        process_data.cli()
        self.assert_processed_correctly()

    def test_cli_url_name(self):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')

        sys.argv = ['python', 'https://github.com/kbrose/dashm-testing.git']

        process_data.cli()
        self.assert_processed_correctly()
