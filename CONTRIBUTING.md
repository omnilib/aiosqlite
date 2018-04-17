# Contributing to aiosqlite

## Preparation

You'll need to have Python 3.5 available for testing
(I recommend using [pyenv][] for this), and a clean
development environment (virtualenv is good).

You can do this with pyenv and virtualenv:

    $ pyenv install 3.5.5
    $ pyenv shell 3.5.5
    $ python3 -m venv .aiosqlite
    $ source .py3/bin/activate
    
    
## Setup

Once in your development environment, install the
appropriate linting tools and dependencies:

    $ cd <path/to/aiosqlite>
    $ make setup
    
    
## Submitting

Before submitting a pull request, please ensure
that you have done the following:

* Documented changes or features in README.md
* Added appropriate license headers to new files
* Written or modified tests for new functionality
* Used [black][] to format code appropriately
* Validated code with `make lint test`

[black]: https://github.com/ambv/black
[pyenv]: https://github.com/pyenv/pyenv
