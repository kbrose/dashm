# -*- coding: utf-8 -*-

"""
Utils to process git repos into something more usable and save
the result back to disk.
"""

import subprocess as sp
from pathlib import Path
import argparse

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
    diff_command = ['git', 'diff', '-n', '1']
    for commit0, commit1 in zip(commits[:-1], commits[1:]):
        with open(dst_path / (commit1 + '.msg'), 'w') as f:
            sp.check_call(message_command + [commit1], stdout=f, cwd=repo_path)
        with open(dst_path / (commit1 + '.diff'), 'w') as f:
            sp.check_call(diff_command + [commit1, commit0],
                          stdout=f, cwd=repo_path)

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
        repo = humanify(repo)
    process(repo)


if __name__ == '__main__':
    cli() # pragma: no cover
