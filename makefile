PKG:=aiosqlite
EXTRAS:=dev,docs

UV:=$(shell uv --version)
ifdef UV
	VENV:=uv venv
	PIP:=uv pip
else
	VENV:=python -m venv
	PIP:=python -m pip
endif

install:
	$(PIP) install -Ue .[$(EXTRAS)]

.venv:
	$(VENV) .venv

venv: .venv
	source .venv/bin/activate && make install
	echo 'run `source .venv/bin/activate` to activate virtualenv'

test:
	python -m coverage run -m $(PKG).tests
	python -m coverage report
	python -m mypy -p $(PKG)

lint:
	python -m flake8 $(PKG)
	python -m ufmt check $(PKG)

format:
	python -m ufmt format $(PKG)

perf:
	python -m unittest -v $(PKG).tests.perf

.PHONY: html
html: .venv README.rst docs/*.rst docs/conf.py
	.venv/bin/sphinx-build -an -b html docs html

.PHONY: clean
clean:
	rm -rf build dist html README MANIFEST *.egg-info

.PHONY: distclean
distclean: clean
	rm -rf .venv
