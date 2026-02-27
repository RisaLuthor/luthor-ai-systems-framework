.PHONY: test lint dev

test:
\tpython -m compileall -q src
\tpytest -q

lint:
\truff check .

dev:
\t./scripts/dev.sh
