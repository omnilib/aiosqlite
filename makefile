build:
	python3 setup.py build

dev:
	python3 setup.py develop

release: lint test clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

setup:
	pip3 install -U mypy pylint twine aiounittest
	if python3 -V | grep "3.[67]"; then pip3 install black; fi

lint:
	if python3 -V | grep "3.[67]"; then which black && black --check . ; fi
	pylint --rcfile .pylint aiosqlite setup.py
	mypy --ignore-missing-imports --no-site-packages .

test:
	python3 -m unittest -v tests

perf:
	python3 -m unittest -v tests.perf

clean:
	rm -rf build dist README MANIFEST aiosqlite.egg-info
