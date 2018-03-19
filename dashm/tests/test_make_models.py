# -*- coding: utf-8 -*-

import io
from contextlib import redirect_stdout

from dashm.models.make_models import make_models


class Test_MakeModels():
    def test_makes_models_without_errors(self):
        trainer, encoder, decoder = make_models(summary=False)

    def test_summary(self):
        f = io.StringIO()
        with redirect_stdout(f):
            make_models(summary=40)
        s = f.getvalue()
        for line in s.split('\n'):
            assert len(line) < 41 # one char lee-way for windows

        f = io.StringIO()
        with redirect_stdout(f):
            make_models(summary=True)
        s = f.getvalue()
        for line in s.split('\n'):
            assert len(line) < 81 # one char lee-way for windows
        assert max(len(line) for line in s.split('\n')) > 75

        f = io.StringIO()
        with redirect_stdout(f):
            make_models(summary=100)
        s = f.getvalue()
        for line in s.split('\n'):
            assert len(line) < 101 # one char lee-way for windows
        assert max(len(line) for line in s.split('\n')) > 90
