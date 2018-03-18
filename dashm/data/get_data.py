# -*- coding: utf-8 -*-

"""
Utils to download data from external sources.
"""

import subprocess as sp
from pathlib import Path
import argparse
from .humanify_git import humanify


def clone(repo, dst=None):
    """
    Clones the git repo at the given destination to
    `<this project>/<dst>/<repo name>`. The destination defaults
    to `data/raw-repos`.

    A file called `<repo name>.dashm` will also be created
    in the destination.

    Inputs
    ------
    repo : str or Path-like
        The path to the git repo, i.e. 'git@github.com:kbrose/dash-m.git'
    dst : str or Path-like
        The destination path relative to the top level of this project.
    """
    if dst is None:
        dst = 'data/raw-repos'
    repo_name = humanify(repo)
    target = Path(__file__).parents[2] / dst / repo_name
    sp.check_call(['git', 'clone', repo, target])
    # create the .dashm file if it does not already exist
    with open(str(target) + '.dashm', 'a'):
        pass


def cli():
    p = argparse.ArgumentParser(description='Clone git repo')
    p.add_argument('repo', type=str,
                   help='The path/URL. See "git clone --help".')
    p.add_argument('dst', default=None, nargs='?',
                   help='Optional destination to clone the repo into.')

    args = p.parse_args()

    clone(args.repo, dst=args.dst)


if __name__ == '__main__':
    cli()
