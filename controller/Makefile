SHELL := /bin/bash

# Make Command for Launching Other Make Recipes
MAKE ?= gmake
# The following lines make the Makefile compatible with linux
ifeq (, $(shell which gmake))
 MAKE=make
endif


VENV ?=.venv
PYTHON=${VENV}/bin/python


.ONESHELL:
.PHONY: create-venv
create-venv:
	if [ -d $(VENV_NAME) ]; then rm -rf $(VENV); fi
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install pip-tools
	$(MAKE) update-venv

.ONESHELL:
.PHONY: sync-venv
sync-venv:
	source $(VENV)/bin/activate
	pip-sync requirements.txt requirements-dev.txt

.ONESHELL:
.PHONY: update-venv
update-venv:
	source $(VENV)/bin/activate
	pip-compile requirements.in --upgrade
	pip-compile requirements-dev.in --upgrade
	$(MAKE) sync-venv


# Get shell in venv
.PHONY: shell
shell:
	. ./$(VENV)/bin/activate && exec $(notdir $(SHELL))

.PHONY: fmt
fmt:
	$(PYTHON) -m isort .
	$(PYTHON) -m black .

.PHONY: lint
lint:
	pip install -e .
	$(PYTHON) -m mypy controller && \
	$(PYTHON) -m flake8 controller && \
	$(PYTHON) -m black --check . && \
	$(PYTHON) -m isort --check .

.PHONY: test
test:
	$(PYTHON) -m pytest tests

.ONESHELL:
.PHONY: run
run:
	source $(VENV)/bin/activate
	kopf run controller/main.py