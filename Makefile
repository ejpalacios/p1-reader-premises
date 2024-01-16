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

requirements/test.txt: pyproject.toml
	poetry export -o requirements/test.txt -f requirements.txt --without-hashes --without main --with test

requirements/dev.txt: pyproject.toml
	poetry export -o requirements/dev.txt -f requirements.txt --without-hashes --without main --with dev

requirements/opt.txt: pyproject.toml
	poetry export -o requirements/opt.txt -f requirements.txt --without-hashes --without main --with opt

# Run utility
run: .venv/bin/activate
	poetry run python -m $(PACKAGE) --config config.yaml

## Sort imports
isort: .venv/bin/activate
	poetry run isort $(PACKAGE) $(TEST) $(TOOLS) --check-only

## Check formatting with black
black: .venv/bin/activate
	poetry run black $(PACKAGE) $(TEST) $(TOOLS) --check

## Mypy static checker
mypy: .venv/bin/activate
	poetry run mypy $(PACKAGE) $(TEST) $(TOOLS) --install-types --non-interactive

## Run tests
test: .venv/bin/activate
	poetry run pytest --cov=$(PACKAGE) -v

## Run local CI
local-ci: isort black mypy test

docker-build: requirements/prod.txt
	docker build -t $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG) . 

docker-push: docker-build
	docker login $(DOCKER_REGISTRY)
	docker push $(DOCKER_REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

## Clean files
clean:
	rm -f requirements.txt
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .venv
