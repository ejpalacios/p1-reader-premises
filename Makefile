.PHONY: isort black mypy test local-ci clean build-local build-registry

IMAGE_NAME := p1-reader
IMAGE_TAG := latest
DOCKER_REGISTRY := docker.io/ejpalacios
PACKAGE := p1reader
TEST := test
TOOLS := utils

## Create virtual environment
.venv/bin/activate: pyproject.toml
	poetry install

## Export requirements file
requirements/prod.txt: pyproject.toml
	poetry export -o requirements/prod.txt -f requirements.txt --without-hashes 

requirements/dev.txt: pyproject.toml
	poetry export -o requirements/dev.txt -f requirements.txt --without-hashes --without main --with dev

requirements/opt.txt: pyproject.toml
	poetry export -o requirements/opt.txt -f requirements.txt --without-hashes --without main --with opt

# Run utility
run: .venv/bin/activate
	poetry run python -m $(PACKAGE) --config config.yaml

## Mypy static checker
.PHONY: mypy
mypy: .venv/bin/activate
	poetry run mypy $(PACKAGE) $(TEST) $(TOOLS) --install-types --non-interactive

## Ruff lint
.PHONY: ruff
ruff: .venv/bin/activate
	poetry run ruff check $(PACKAGE) $(TEST) $(TOOLS)

## Run tests
test: .venv/bin/activate
	poetry run pytest --cov=$(PACKAGE) -v --cov-report term-missing

## Run local CI
local-ci: ruff mypy test

docker-build: requirements/prod.txt
	docker build -t $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) . 

docker-push: docker-build
	docker login $(DOCKER_REGISTRY)
	docker push $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

## Clean files
clean:
	rm -rf  requirements/*.txt
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .venv
