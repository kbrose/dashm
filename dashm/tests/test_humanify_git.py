# -*- coding: utf-8 -*-

from dashm.data import humanify_git


class Test_Humanify():
    def test_humanify(self):
        url = 'git@github.com:kbrose/dashm-testing.git'
        assert humanify_git.humanify(url) == 'dashm-testing'

        url = 'git@something-else.org:no-path.git'
        assert humanify_git.humanify(url) == 'no-path'
