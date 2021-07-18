FILES :=

all: $(FILES)
.PHONY: all

clean:
	rm -f $(FILES)
.PHONY: clean

format:
	black .
.PHONY: format

test:
	rl runtests
.PHONY: test

