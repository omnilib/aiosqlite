README:
	cp README.rst README

build:
	python3 setup.py build

dev:
	python3 setup.py develop

upload:
	python3 setup.py sdist upload

lint:
	python3 -m flake8 --show-source .
	mypy --ignore-missing-imports .

test:
	python3 -m unittest tests

clean:
	rm -rf build dist README MANIFEST aiosqlite.egg-info
