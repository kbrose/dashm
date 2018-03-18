[![Build Status](https://travis-ci.org/kbrose/dashm.svg?branch=master)](https://travis-ci.org/kbrose/dashm)

Tired of `git commit -m "an unhelpful commit message"`? Use `dashm` to
create that commit message for you!

Full disclosure nothing is finished yet. This is an aspirational repo.

# Downloading and prepping data

Usage:

```
make raw repo=<repo name>
make process repo=<repo name/short name>
```

Example:

```
make process repo=git@github.com:kbrose/dashm-testing.git
```
