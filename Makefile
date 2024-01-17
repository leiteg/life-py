all: check fix format
	
check:
	@ruff check

fix:
	@ruff check --fix

format:
	@ruff format

test:
	@pytest

type-check:
	@mypy -p life

.PHONY: all check fix format test type-check
