.PHONY: install test lint run docker-build docker-run

install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .

run:
	uvicorn laf.api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t luthor-ai-systems-framework:dev .

docker-run:
	docker run --rm -p 8000:8000 luthor-ai-systems-framework:dev
