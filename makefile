build:
	python3 setup.py build

dev:
	python3 setup.py develop

release: lint test clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

make setup:
	pip3 install -U mypy pylint twine
	python3 -V | grep "3.[67]" && pip3 install black || true

lint:
	python3 -V | grep "3.[67]" && which black && black --check aiosqlite || true
	pylint --rcfile .pylint aiosqlite setup.py
	mypy --ignore-missing-imports --python-version 3.5 --no-site-packages .
	mypy --ignore-missing-imports --python-version 3.6 --no-site-packages .

test:
	python3 tests/smoke.py
	python3 -m unittest tests

clean:
	rm -rf build dist README MANIFEST aiosqlite.egg-info
