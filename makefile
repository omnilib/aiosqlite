venv:
	python -m venv .venv
	source .venv/bin/activate && make setup dev
	echo 'run `source .venv/bin/activate` to develop aiosqlite'

setup:
	python -m pip install -Ur requirements-dev.txt
	if python -V | grep -v "3.5"; then python -m pip install -U black; fi

dev:
	python setup.py develop
	
release: lint test clean
	python setup.py sdist
	python -m twine upload dist/*

format:
	python -m isort --apply --recursive aiosqlite setup.py
	python -m black aiosqlite setup.py

lint:
	python -m pylint --rcfile .pylint aiosqlite/*.py setup.py
	if python -V | grep -v "3.5"; then python -m isort --diff --recursive aiosqlite setup.py; fi
	if python -V | grep -v "3.5"; then python -m black --check aiosqlite setup.py; fi

test:
	python -m coverage run -m aiosqlite.tests
	python -m coverage report
	python -m mypy aiosqlite/*.py

perf:
	python -m unittest -v aiosqlite.tests.perf

clean:
	rm -rf build dist README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv
