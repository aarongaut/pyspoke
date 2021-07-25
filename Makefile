all: dist
.PHONY: all

publish: dist
	python3 -m twine upload dist/*
.PHONY: publish

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
	dev-bin/rl runtests tests
	python3 -m build

