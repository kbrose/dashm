# -*- coding: utf-8 -*-

import argparse


def humanify(url):
    """
    Take the human-ish part out of a Git URL.
    """
    if url.endswith('.git'):
        url = url[:-len('.git')]
    if ':' in url:
        url = url.split(':')[-1]
    return url.split('.git')[0].split('/')[-1]


def cli():
    p = argparse.ArgumentParser(description='Humanify the name of a git repo')
    p.add_argument('repo', type=str,
                   help='The path/URL. See "git clone --help".')

    args = p.parse_args()

    print(humanify(args.repo), end='')


if __name__ == '__main__':
    cli()
