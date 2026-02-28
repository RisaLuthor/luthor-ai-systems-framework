.PHONY: test lint dev

test:
	python -m compileall -q src
	pytest -q

lint:
	ruff check .

dev:
	./scripts/dev.sh
