.PHONY: raw process clean

# TODO: make this not yell at you if $(repo) is empty
human_repo_name=$(shell python -m dashm.data.humanify_git $(repo))

raw: data/raw-repos/$(human_repo_name).dashm

data/raw-repos/$(human_repo_name).dashm:
	python -m dashm.data.get_data $(repo)

process: raw data/processed-repos/$(human_repo_name).dashm

data/processed-repos/$(human_repo_name).dashm:
	python -m dashm.data.process_data $(human_repo_name)

clean-data:
	rm -rf data/raw-repos/*
	rm -rf data/processed-repos/*

clean-code:
	rm -rf *.pyc
	rm -rf .pytest_cache
	rm -rf dashm/.pytest_cache

test: clean-code
	python -m pytest
