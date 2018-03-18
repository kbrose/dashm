# -*- coding: utf-8 -*-

import subprocess as sp
import pathlib


def clone(repo, dst='data/raw-repos'):
    """
    Clones the git repo at the given destination to
    `<this project>/<dst>/<repo name>`. The destination defaults
    to `data/raw-repos`.

    Inputs
    ------
    repo : str or Path-like
        The path to the git repo, i.e. 'git@github.com:kbrose/dash-m.git'
    dst : str or Path-like
        The destination path relative to the top level of this project.
    """
    repo_name = repo.split('.git')[0].split('/')[-1]
    target = pathlib.Path(__file__).parents[2] / dst / repo_name
    sp.check_call(['git', 'clone', repo, target])
