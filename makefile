build:
	python3 setup.py build

dev:
	python3 setup.py develop

upload: lint test clean
	python3 setup.py sdist upload

make setup:
	pip3 install mypy pylint
	python3 -V | grep "3.[67]" && pip3 install black || true

lint:
	python3 -V | grep "3.[67]" && which black && black --check aiosqlite || true
	pylint --rcfile .pylint aiosqlite
	mypy --ignore-missing-imports --python-version 3.5 .
	mypy --ignore-missing-imports --python-version 3.6 .

test:
	python3 tests/smoke.py
	python3 -m unittest tests

clean:
	rm -rf build dist README MANIFEST aiosqlite.egg-info
