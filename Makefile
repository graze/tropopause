DOCKER := $(shell which docker)
DOCKERUN := $(DOCKER) run -it -v $(CURDIR):/python graze/tropopause
PYDIRS := setup.py examples tests tropopause

.PHONY: setup
setup: ## Create Docker container for development.
	${DOCKER} build -t graze/tropopause:latest -f Dockerfile .

.PHONY: lint
lint: ## Run pycodestyle and pyflakes against the code.
	@$(DOCKERUN) pycodestyle ${PYDIRS}
	@$(DOCKERUN) pyflakes ${PYDIRS}

.PHONY: test
test: ## Run all tests and output coverage to the console.
	@$(DOCKERUN) python setup.py test

.PHONY: build
build: ## Build the Library with setuptools.
	@$(DOCKERUN) python setup.py build

.PHONY: install
install: ## Install the Library in the container.
	@$(DOCKERUN) python setup.py install

.DEFAULT: all
.PHONY: all
all: ## Test, build & install the library.
all: test build install

.SILENT: help
.PHONY: help
help: ## Show this help message
	set -x
	echo "Usage: make [target] ..."
	echo ""
	echo "Available targets:"
	egrep '^(.+)\:\ ##\ (.+)' ${MAKEFILE_LIST} | column -t -c 2 -s ':#' | sort