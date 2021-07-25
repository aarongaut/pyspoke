all: test dist
.PHONY: all

release: dist
	python3 -m twine upload dist/*
.PHONY: release

clean:
	rm -rf dist
.PHONY: clean

format:
	black .
.PHONY: format

test:
	dev-bin/rl runtests tests
.PHONY: test

dist: $(shell find src) LICENSE pyproject.toml README.md setup.cfg
	python3 -m build

