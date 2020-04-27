venv:
	python -m venv .venv
	source .venv/bin/activate && make setup dev
	echo 'run `source .venv/bin/activate` to develop aiosqlite'

setup:
	python -m pip install -Ur requirements-dev.txt
	if python -V | grep -v "3.5"; then python -m pip install -U black; fi

dev:
	flit install --symlink

release: lint test clean
	flit publish

format:
	python -m isort --apply --recursive aiosqlite
	python -m black aiosqlite

lint:
	python -m pylint --rcfile .pylint aiosqlite/*.py
	if python -V | grep -v "3.5"; then python -m isort --diff --recursive aiosqlite; fi
	if python -V | grep -v "3.5"; then python -m black --check aiosqlite; fi

test:
	python -m coverage run -m aiosqlite.tests
	python -m coverage report
	python -m mypy aiosqlite/*.py

perf:
	python -m unittest -v aiosqlite.tests.perf

html: docs/*.rst docs/conf.py
	sphinx-build -b html docs html

clean:
	rm -rf build dist html README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv
