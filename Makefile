# """
# __author__ = "Sky UK Ltd"
# __copyright__ = Copyright © Sky CP Limited 2023.
# All rights reserved. No part of this work may be reproduced,
# stored in a retrieval system of any nature, or transmitted,
# in any form or by any means including photocopying
# and recording, without the prior written permission of Sky,
# the copyright owner.
# __licence__ = "subject to the terms of the licence with Sky UK Ltd'
# __version__ = "1.0"
# """
PROJECT=connectors
TAG="ipnd/netauto/${PROJECT}"
REGISTRY = "${FC_REGISTRY}/ipnd-dne/${PROJECT}"


# setting the GIT_BRANCH to the current branch on git
GIT_BRANCH:=$(or $(CI_COMMIT_REF_NAME), $(shell git symbolic-ref --short HEAD))

# setting the branch variable to either CONNECTOR_BRANCH or GIT_BRANCH, preference is given to CONNECTOR_BRANCH
BRANCH:=$(or $(CONNECTORS_BRANCH), $(GIT_BRANCH))

# Default python: 3.10
PY := py310


# prompt_example> make test PY=py310 OPTIONS="-- -s"
.PHONY: test
test:
	@tox -e $(PY) $(OPTIONS)


.PHONY: coverage
coverage:
	@tox -e coverage


.PHONY: deploy-coverage
deploy-coverage:
	@tox -e deploy-coverage


.PHONY: isort
isort:
	@tox -e isort


.PHONY: lint
lint:
	@tox -e lint


# prompt_example> make bumpversion OPTIONS="-- --allow-dirty patch"
.PHONY: bumpversion
bumpversion:
	@tox -e bumpversion $(OPTIONS)


.PHONY: find_todo
find_todo:
	@grep --color=always -PnRe "(#|\"|\').*TODO" src/ || true


.PHONY: find_fixme
find_fixme:
	@grep --color=always -nRe "#.*FIXME" src/ || true


.PHONY: find_xxx
find_xxx:
	@grep --color=always -nRe "#.*XXX" src/ || true


.PHONY: count
count: clean
	@# @find src/ -type f \( -name "*.py" -o -name "*.rst" \) | xargs wc -l
	@echo "Lines of documentation:"
	@find docs/source/ -type f -name "*.rst" | xargs wc -l
	@echo "Lines of code:"
	@find src/ tests/ -type f -name "*.py" | xargs wc -l


.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' | xargs rm -rf
	@find . -type d -name '*.ropeproject' | xargs rm -rf
	@rm -rf build/
	@rm -rf dist/
	@rm -f src/*.egg
	@rm -f src/*.eggs
	@rm -rf src/*.egg-info/
	@rm -f MANIFEST
	@rm -rf docs/build/
	@rm -rf htmlcov/
	@rm -f .coverage
	@rm -f .coverage.*
	@rm -rf .cache/
	@rm -f coverage.xml
	@rm -f *.cover
	@rm -rf .pytest_cache/


.PHONY: install-dev
install-dev:
	@pip install -e .


##### Build #####

.PHONY: build-python-source
build-python-source:
	@python setup.py sdist



##### Docker #####

.PHONY: build-docker
build-docker: clean build-python-source build-pip-dependencies _build-docker

.PHONY: build-pip-dependencies
build-pip-dependencies:
	@pip download --no-deps -d dist/ -r scm_requirements.txt



.PHONY: _build-docker
_build-docker:
	@docker build -t ${REGISTRY}:${BRANCH} --build-arg https_proxy=${https_proxy} --build-arg http_proxy=${http_proxy} -f docker/Dockerfile . --no-cache

##### Docker #####

.PHONY: run-docker
run-docker:
	@docker run --rm -d --name=connectors-${BRANCH} -e CONNECTORS_ITSM_SUBSCRIPTION_KEY="${CONNECTORS_ITSM_SUBSCRIPTION_KEY}" -e CONNECTORS_CAUTH_USERNAME="${CONNECTORS_CAUTH_USERNAME}" -e CONNECTORS_AD_PASSWORD="${CONNECTORS_AD_PASSWORD}" -e CONNECTORS_CAUTH_PASSWORD="${CONNECTORS_CAUTH_PASSWORD}" -e CONNECTORS_AD_USERNAME="${CONNECTORS_AD_USERNAME}" -e CONNECTORS_OAUTH_PASSWORD="${CONNECTORS_OAUTH_PASSWORD}" -e CONNECTORS_OAUTH_USERNAME="${CONNECTORS_OAUTH_USERNAME}" -p 5000:5000 ${REGISTRY}:${BRANCH}

.PHONY: kill-docker
kill-docker:
	@docker kill connectors-${BRANCH}

##### docker login, push to FC registry #####
# Create two new environment variable as
# FC_USERNAME= username e.g. rky08
# FC_PASSWORD= password

.PHONY: login-registry-fc
login-registry-fc:
	@docker login ${FC_REGISTRY} -u ${FC_USERNAME}


.PHONY: push-registry-fc
push-registry-fc:
	@docker push ${REGISTRY}:${BRANCH}


##### Run #####
# App needs to be installed (can use -e)

.PHONY: run-dev-server
run-dev-server:
	@CONNECTORS_CONFIG=$(shell pwd)/docker/connectors/config/connectors.conf FLASK_APP=src/connectors.uwsgi:app FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=9000


.PHONY: run-server
run-server:
	@uwsgi --http :9000 --module connectors.wsgi:app --disable-logging


##### Docs #####

.PHONY: docs-html
docs-html:
	@tox -e docs-html


.PHONY: docs-singlehtml
docs-singlehtml:
	@tox -e docs-singlehtml


.PHONY: docs-pdf
docs-pdf:
	@tox -e docs-pdf

.PHONY: code-formatter-check
code-formatter-check:
	@tox -e code-formatter-check


.PHONY: code-formatter
code-formatter:
	@tox -e code-formatter


.PHONY: generate-openapi
generate-openapi:
	@tox -e generate-openapi

.PHONY: validate-openapi
validate-openapi:
	@tox -e validate-openapi


### pre-commit ###

# Determine the new branch name. If CI_COMMIT_REF_NAME is not set, 
# use the current branch name obtained from git rev-parse.
NEW_BRANCH=$(or $(CI_COMMIT_REF_NAME) , $(shell git rev-parse --abbrev-ref HEAD))
# Determine the origin branch name. If CI_MERGE_REQUEST_TARGET_BRANCH_NAME is set,
# use it. Otherwise, use CI_DEFAULT_BRANCH. If both are not set, default to 'origin'.
ORIGIN=$(or $(CI_MERGE_REQUEST_TARGET_BRANCH_NAME) , $(CI_DEFAULT_BRANCH) , origin)
# Count the number of commits between HEAD and the origin branch.
NUMBER_OF_COMMITS=$(shell git rev-list --count HEAD ^$(ORIGIN))
# Obtain the list of files that have been committed in the specified number of commits.
# Filter out empty lines and remove duplicates.
COMMITED_FILES=$(shell git log -n $(NUMBER_OF_COMMITS) --pretty=format: --name-only | grep -vE '^$$' | sort -u )
# Obtain the list of untracked files.
UNTRACKED_FILES=$(shell git ls-files --others --exclude-standard)
# Obtain the list of changed files between the current branch and its first parent commit,
# and combine it with untracked and committed files.
# The `2>/dev/null` at the end redirects standard error (stderr) output to /dev/null,
CHANGED_FILES=$(shell git diff --name-only $(NEW_BRANCH)^0 2>/dev/null)
COMBINED_CHANGED_FILES=$(CHANGED_FILES) $(UNTRACKED_FILES) $(COMMITED_FILES)
# Make the list of changed files unique by sorting and removing duplicates.
UNIQUE_CHANGED_FILES=$(shell echo $(sort $(COMBINED_CHANGED_FILES)) | uniq)

# This target is used for the pre-commit hook.
# It echos out information about the origin, new branch, number of commits, and modified files.
# Then it runs the pre-commit checks only on the unique modified files.
.PHONY: pre-commit
pre-commit:
	@echo "ORIGIN: " ${ORIGIN}
	@echo "New branch: " ${NEW_BRANCH}
	@echo "Number of commits: " ${NUMBER_OF_COMMITS}
	@echo "Checking modified files: " ${UNIQUE_CHANGED_FILES}
	@pre-commit run --files ${UNIQUE_CHANGED_FILES}