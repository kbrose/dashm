import os
import pathlib
import shutil

from dashm.data import get_data


class TestClone():
    @classmethod
    def setup_method(cls):
        cls.tmp_dst = pathlib.Path(__file__).parents[0] / 'tmp-data/'
        os.makedirs(cls.tmp_dst, exist_ok=True)

    @classmethod
    def teardown_method(cls):
        shutil.rmtree(cls.tmp_dst)

    def test_clone(self):
        get_data.clone('git@github.com:kbrose/math.git', self.tmp_dst)
        assert os.path.exists(self.tmp_dst)
        assert os.path.exists(pathlib.Path(self.tmp_dst) / 'math/.git')
