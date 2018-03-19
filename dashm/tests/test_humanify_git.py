# -*- coding: utf-8 -*-

import sys
import io
from contextlib import redirect_stdout

from dashm.data import humanify_git


class Test_Humanify():
    @classmethod
    def setup_method(cls):
        old_sys_argv = sys.argv
        sys.argv = old_sys_argv

    teardown_method = setup_method

    def test_humanify_ssh(self):
        url = 'git@github.com:kbrose/dashm-testing.git'
        assert humanify_git.humanify(url) == 'dashm-testing'

    def test_humanify_https(self):
        url = 'https://github.com/kbrose/dashm-testing.git'
        assert humanify_git.humanify(url) == 'dashm-testing'

    def test_humanify_no_slashes(self):
        url = 'git@something-else.org:no-path.git'
        assert humanify_git.humanify(url) == 'no-path'

    def test_cli_https(self):
        sys.argv = ['python', 'https://github.com/kbrose/dashm-testing.git']
        f = io.StringIO()
        with redirect_stdout(f):
            humanify_git.cli()
        s = f.getvalue()
        assert s == 'dashm-testing'

    def test_cli_ssh(self):
        sys.argv = ['python', 'git@github.com:kbrose/dashm-testing.git']
        f = io.StringIO()
        with redirect_stdout(f):
            humanify_git.cli()
        s = f.getvalue()
        assert s == 'dashm-testing'
