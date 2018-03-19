# -*- coding: utf-8 -*-

import os
from glob import glob
from pathlib import Path
import shutil

import pytest

from dashm.data import get_data
from dashm.data import process_data
from dashm.models import train
from dashm.models import predict

TEST_STRING = b'''diff --git a/Makefile b/Makefile
index 9917f99..8a30d76 100644
--- a/Makefile
+++ b/Makefile
@@ -13,6 +13,12 @@ process: raw data/processed-repos/$(human_repo_name).dashm
 data/processed-repos/$(human_repo_name).dashm:
        python -m dashm.data.process_data $(human_repo_name)

+model: data/processed-repos/$(human_repo_name).dashm
+ python -m dashm.models.train $(human_repo_name)
+
+test: clean-code
+ python -m pytest
+
 clean-all: clean-code clean-data

 clean-data: clean-raw clean-processe
'''


class Test_Predict():
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

    def test_predict(self):
        get_data.clone('https://github.com/kbrose/dashm-testing.git')
        process_data.process('dashm-testing')
        train.train('dashm-testing', steps_per_epoch=3, epochs=1)

        predictor_inferred = predict.Predictor()

        probs = predictor_inferred.predict_proba(TEST_STRING)
        preds = predictor_inferred.predict(TEST_STRING)

        assert len(probs) == len(preds)

        predictor_explicit = predict.Predictor('*dashm-testing')

        probs = predictor_explicit.predict_proba(TEST_STRING)
        preds = predictor_explicit.predict(TEST_STRING)

        assert len(probs) == len(preds)

    def test_predict_raises_when_not_found(self):
        with pytest.raises(RuntimeError):
            predict.Predictor('!@#$%^&*()_+')
