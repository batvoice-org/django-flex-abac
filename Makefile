MAIN_BRANCH=master
CURRENT_VERSION = $(shell cat VERSION)
CURRENT_BRANCH = $(shell git branch --show-current)

# VERSION_SUFFIX is overwritten to be "" when the current branch is master
VERSION_SUFFIX ?= "+dev.$(shell git describe --abbrev=8 --always HEAD | cut -d- -f2-).$(shell date +%s)"
ifeq ($(CURRENT_BRANCH),$(MAIN_BRANCH))
	undefine VERSION_SUFFIX
endif

.upgrade-pip:
	pip install --upgrade pip

install: .upgrade-pip	## Installs the library in the current environment.
	pip install -e .

install-docs: .upgrade-pip
	pip install -e .[doc]
	cd docs && make html

install-all: .upgrade-pip install install-docs	## Installs the library in the current environment, all kind of requirements.

clean:		## Cleans everything
	rm -rf build dist *.egg-info docs/_build
	find . -name __pycache__ -type d | xargs rm -rf

test: install		## Launches the tests.
	python example/backend/manage.py test --keepdb --parallel $(shell nproc)

test-failfast: install		## Launches the tests.
	python example/backend/manage.py test --keepdb --parallel $(shell nproc) --failfast

.upgrade-version:
	$(eval MINOR_VERSION := $(shell echo $(CURRENT_VERSION) | cut -d+ -f1 | cut -d. -f3))
# We just increase minor if it is an "official" version (MAIN_BRANCH)
ifeq ($(strip $(CURRENT_BRANCH)$(VERSION_SUFFIX)),$(MAIN_BRANCH))
	$(eval MINOR_VERSION := $(shell expr $(MINOR_VERSION) + 1))
endif
	$(eval CURRENT_VERSION := "$(shell echo $(CURRENT_VERSION) | cut -d+ -f1 | cut -d. -f-2).$(MINOR_VERSION)$(VERSION_SUFFIX)")
	echo $(CURRENT_VERSION) > VERSION

build-library: clean .upgrade-version 			## Builds the library
	python setup.py sdist

push-library:		# Pushes the library
	pip install twine
	twine upload -r batvoice dist/* --skip-existing

.attempt_release: build-library## Defines a new release tag and pushes it into the main branch of the repository.
ifeq ($(strip $(CURRENT_BRANCH)$(VERSION_SUFFIX)),$(MAIN_BRANCH))
	git add VERSION
	git commit -m "Upgrading library version to $(CURRENT_VERSION)"
	git tag -a $(CURRENT_VERSION) -m "Release for version $(CURRENT_VERSION)"
	git push
	git push --tags
	make push-library
else
ifneq ($(strip $(CURRENT_BRANCH)),$(MAIN_BRANCH))
	@echo "You should be in the main branch to do this! Current branch: $(CURRENT_BRANCH)"
else
	@echo "You should not be using a suffix in your version name to do this! Current suffix: $(VERSION_SUFFIX)"
endif
endif

release:
	cp VERSION VERSION.old
	make .attempt_release || (cp VERSION.old VERSION && exit -1)
	rm VERSION.old || true

help:   ## Shows available commands.
	@echo "Available commands:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?##[\s]?.*$$' --no-filename $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?##"}; {printf "    make \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo
