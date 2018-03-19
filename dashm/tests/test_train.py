# -*- coding: utf-8 -*-

import os
from glob import glob
from pathlib import Path
import shutil

from dashm.data import get_data
from dashm.data import process_data
from dashm.models import train


class Test_Train():
    @classmethod
    def setup_method(cls):
        data_path = Path(__file__).parents[2] / 'data/'
        for interim in ['raw-repos', 'processed-repos']:
            dst = data_path / interim / 'dashm-testing'
            try:
                shutil.rmtree(dst)
            except FileNotFoundError:
                pass
            try:
                os.remove(str(dst) + '.dashm')
            except FileNotFoundError:
                pass

        cls.models_path = Path(__file__).parents[1] / 'models/saved'
        dashm_testing_folders = glob(str(cls.models_path / '*dashm-testing'))
        for dashm_testing_folder in dashm_testing_folders:
            shutil.rmtree(dashm_testing_folder)

    teardown_method = setup_method

    def test_train(self):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')
        process_data.process('dashm-testing')

        train.train('dashm-testing', steps_per_epoch=3, epochs=1)

        saved_folders = glob(str(self.models_path / '*dashm-testing'))
        assert len(saved_folders)

        for folder in saved_folders:
            all_filenames = [os.path.split(f)[-1]
                             for f in glob(str(Path(folder) / '*'))]
            assert 'trainer.h5' in all_filenames
            assert 'encoder.h5' in all_filenames
            assert 'decoder.h5' in all_filenames


class Test_CLI():
    pass
