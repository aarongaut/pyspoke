all:
.PHONY: all

format:
	black .
.PHONY: format

test:
	bin/rl runtests tests
.PHONY: test

