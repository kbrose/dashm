import os
from pathlib import Path
import shutil
from glob import glob

from dashm.data import get_data
from dashm.data import process_data

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

    teardown_method = setup_method

    def test_clone(self):
        get_data.clone('git@github.com:kbrose/dashm-testing.git')
        process_data.process('dashm-testing')

        dst = self.data_path / 'processed-repos/dashm-testing'
        assert os.path.exists(dst)

        expected_files = Path(__file__).parents[0] / 'data/dashm-testing/*'
        actual_files = [os.path.split(x)[-1] for x in glob(str(dst / '*'))]
        for f in glob(str(expected_files)):
            assert os.path.split(f)[-1] in actual_files
            with open(f) as fp:
                expected_contents = fp.read()
            with open(dst / os.path.split(f)[-1]) as fp:
                actual_contents = fp.read()
            assert expected_contents == actual_contents
