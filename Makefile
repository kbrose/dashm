.PHONY: raw process clean-data clean-raw clean-processed clean-code test

human_repo_name=$(shell if [ $(repo) ]; then python -m dashm.data.humanify_git \
		$(repo); else echo IF_YOU_SEE_THIS_SPECIFY_repo_AS_ARG; fi)

raw: data/raw-repos/$(human_repo_name).dashm

data/raw-repos/$(human_repo_name).dashm:
	python -m dashm.data.get_data $(repo)

process: data/raw-repos/$(human_repo_name).dashm data/processed-repos/$(human_repo_name).dashm

data/processed-repos/$(human_repo_name).dashm:
	python -m dashm.data.process_data $(human_repo_name)

model: process
	python -m dashm.models.train $(human_repo_name) 0.9

test: clean-code
	python -m pytest --cov-report term-missing --cov=dashm

clean-all: clean-code clean-data clean-models

clean-data: clean-raw clean-processed

clean-raw:
	rm -rf data/raw-repos/*

clean-processed:
	rm -rf data/processed-repos/*

clean-code:
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf dashm/.pytest_cache

clean-models:
	rm -rf dashm/models/saved/*
