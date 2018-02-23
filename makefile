README:
	cp README.rst README

build:
	python3 setup.py build

dev:
	python3 setup.py develop

upload: lint test clean
	python3 setup.py sdist upload

lint:
	pylint --rcfile .pylint aiosqlite
	mypy --ignore-missing-imports --python-version 3.5 .
	mypy --ignore-missing-imports --python-version 3.6 .

test:
	python3 tests/smoke.py
	python3 -m unittest tests

clean:
	rm -rf build dist README MANIFEST aiosqlite.egg-info
