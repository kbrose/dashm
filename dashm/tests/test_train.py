# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil
import sys

from dashm.data import get_data
from dashm.data import process_data
from dashm.models import train


class Test_Train():
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

    @classmethod
    def _clean(cls):
        cls.models_path = Path(__file__).parents[1] / 'models/saved'
        dashm_testing_folders = cls.models_path.glob('*dashm-testing')
        for dashm_testing_folder in dashm_testing_folders:
            shutil.rmtree(dashm_testing_folder)

    @classmethod
    def setup_method(cls):
        cls.__old_sys_argv = sys.argv
        cls._clean()

    @classmethod
    def teardown_method(cls):
        cls._clean()
        sys.argv = cls.__old_sys_argv

    def test_train(self):
        train.train('dashm-testing', 0.5, steps_per_epoch=3, epochs=2)

        saved_folders = list(self.models_path.glob('*dashm-testing'))
        assert len(saved_folders)

        for folder in saved_folders:
            all_filenames = [os.path.split(f)[-1]
                             for f in Path(folder).glob('*')]
            assert 'trainer.h5' in all_filenames
            assert 'encoder.h5' in all_filenames
            assert 'decoder.h5' in all_filenames

    def test_cli(self):
        sys.argv = ['train.py', 'dashm-testing', '0.5', '--steps_per_epoch',
                    '3', '--epochs', '1']
        train.cli()

        saved_folders = list(self.models_path.glob('*dashm-testing'))
        assert len(saved_folders)

        for folder in saved_folders:
            all_filenames = [os.path.split(f)[-1]
                             for f in Path(folder).glob('*')]
            assert 'trainer.h5' in all_filenames
            assert 'encoder.h5' in all_filenames
            assert 'decoder.h5' in all_filenames
