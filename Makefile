VERSION = $(shell dev-bin/rl python -c 'from spoke.version import __version__ as v; print(v, end="")')

all: dist
.PHONY: all

install: dist
	python3 -m pip install --force-reinstall dist/pyspoke-$(VERSION)-py3-none-any.whl
.PHONY: install

publish: test dist
	python3 -m twine upload dist/*
.PHONY: publish

clean:
	rm -rf dist
	rm -rf src/*.egg-info
	find src -name __pycache__ -type d -prune -exec rm -r {} ';'
	find tests -name artifacts -type d -prune -exec rm -r {} ';'
.PHONY: clean

format:
	black .
.PHONY: format

test:
	dev-bin/rl runtests tests
.PHONY: test

dist: $(shell find src) LICENSE pyproject.toml README.md setup.cfg
	python3 -m build

