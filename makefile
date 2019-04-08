venv:
	python3 -m venv .venv

setup:
	pip3 install -U mypy pylint twine aiounittest coverage codecov
	if python3 -V | grep "3.[67]"; then pip3 install black; fi

dev: venv
	source .venv/bin/activate && make setup
	source .venv/bin/activate && python3 setup.py develop
	@echo 'Run `source .venv/bin/activate` to develop aiosqlite'

release: lint test clean
	python3 setup.py sdist
	python3 -m twine upload dist/*

lint:
	mypy --ignore-missing-imports --no-site-packages aiosqlite
	pylint --rcfile .pylint aiosqlite tests setup.py
	if python3 -V | grep "3.[67]"; then which black && black --check . ; fi

test:
	python3 -m coverage run -m tests
	python3 -m coverage report

perf:
	python3 -m unittest -v tests.perf

clean:
	rm -rf build dist README MANIFEST aiosqlite.egg-info

distclean: clean
	rm -rf .venv
