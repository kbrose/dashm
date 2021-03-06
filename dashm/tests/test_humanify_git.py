# -*- coding: utf-8 -*-

import sys
import io
from contextlib import redirect_stdout

from dashm.data import humanify_git


class Test_Humanify():
    @classmethod
    def setup_method(cls):
        cls.__old_sys_argv = sys.argv

    @classmethod
    def teardown_method(cls):
        sys.argv = cls.__old_sys_argv

    @staticmethod
    def test_humanify_ssh():
        url = 'git@github.com:kbrose/dashm-testing.git'
        assert humanify_git.humanify(url) == 'dashm-testing'

    @staticmethod
    def test_humanify_https():
        url = 'https://github.com/kbrose/dashm-testing.git'
        assert humanify_git.humanify(url) == 'dashm-testing'

    @staticmethod
    def test_humanify_no_slashes():
        url = 'git@something-else.org:no-path.git'
        assert humanify_git.humanify(url) == 'no-path'

    @staticmethod
    def test_cli_https():
        sys.argv = ['python', 'https://github.com/kbrose/dashm-testing.git']
        f = io.StringIO()
        with redirect_stdout(f):
            humanify_git.cli()
        s = f.getvalue()
        assert s == 'dashm-testing'

    @staticmethod
    def test_cli_ssh():
        sys.argv = ['python', 'git@github.com:kbrose/dashm-testing.git']
        f = io.StringIO()
        with redirect_stdout(f):
            humanify_git.cli()
        s = f.getvalue()
        assert s == 'dashm-testing'
