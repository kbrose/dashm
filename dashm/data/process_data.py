# -*- coding: utf-8 -*-

import subprocess as sp
from pathlib import Path
import argparse

from . import get_data
from .humanify_git import humanify


def process(repo_path):
    """
    Processes the commits in the git repo found at `repo_path`.
    If `repo_path` is not absolute, then it is assumed to be
    a folder in `<project path>/data/raw-repos/`.

    The processed data is output to
    `<project path>/data/processed-repos/<repo name>`. The processed
    data is a set of files of the form

        <commit-hash>.msg
        <commit-hash>.diff

    A file called `<repo name>.dashm` will also be created
    in the destination.

    Inputs
    ------
    repo : str or Path-like
        The path to the git repo. Either an absolute path, or
        a folder within `<project path>/data/raw-repos`.
    """
    repo_path = Path(repo_path)
    if not repo_path.is_absolute():
        repo_path = Path(__file__).parents[2] / 'data/raw-repos' / repo_path

    dst_path = Path(__file__).parents[2] / 'data/processed-repos'
    dst_path /= repo_path.parts[-1]
    dst_path.mkdir(parents=True, exist_ok=True)

    commits = sp.check_output(['git', 'log', '--pretty=%H'], cwd=repo_path)
    commits = commits.decode('ascii').split()

    message_command = ['git', 'log', '--pretty=%B', '-n', '1']
    diff_command = ['git', 'diff']
    for commit in commits:
        with open(dst_path / (commit + '.msg'), 'w') as f:
            sp.check_call(message_command + [commit], stdout=f, cwd=repo_path)
        with open(dst_path / (commit + '.diff'), 'w') as f:
            sp.check_call(diff_command + [commit], stdout=f, cwd=repo_path)

    # create the .dashm file if it does not already exist
    with open(str(dst_path) + '.dashm', 'a'):
        pass


def cli():
    p = argparse.ArgumentParser(
        description='Process git repo into a more usable format'
    )
    p.add_argument('repo', type=str,
                   help=('Absolute path to repo, or folder name of a folder'
                         ' that exists in "<project path>/data/raw-repos/".'
                         ' Alternatively, can be a git repo where we will'
                         ' use the human-ish portion of the git repo.'))

    args = p.parse_args()

    repo = args.repo
    if ':' in repo:
        repo = get_data.humanify(repo)
    process(args.repo)


if __name__ == '__main__':
    cli()
