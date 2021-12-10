PROJECT := <insert-project>
IMAGE := gcr.io/$(PROJECT)/webhook:0.0.17

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
	$(PYTHON) -m mypy webhook && \
	$(PYTHON) -m flake8 webhook && \
	$(PYTHON) -m black --check . && \
	$(PYTHON) -m isort --check .

.PHONY: test
test:
	$(PYTHON) -m pytest tests

.PHONY: build
build:
	@DOCKER_BUILDKIT=1 docker build . \
	-t $(IMAGE) \
	-f ./Dockerfile


.PHONY: push
push:
	docker push $(IMAGE)

.PHONY: build-push
build-push: build push