# Contributing to aiosqlite

## Preparation

You'll need to have at least Python 3.5 available for testing.
Python 3.6 or newer is recommended in order to validate formatting.

You can do this with [pyenv][]:

    $ pyenv install 3.6.10
    $ pyenv local 3.6.10
    
    
## Setup

Once cloned, create a clean virtual environment and
install the appropriate tools and dependencies:

    $ cd <path/to/aiosqlite>
    $ make venv
    $ source .venv/bin/activate


## Formatting

aiosqlite uses *[black][]* and [isort][] for formatting code
and imports, respectively. If your editor does not already
support this workflow, you can manually format files:

    $ make format


## Testing

Once you've made changes, you should run unit tests,
validate your type annotations, and ensure your code
meets the appropriate style and linting rules:

    $ make test lint
    
    
## Submitting

Before submitting a pull request, please ensure
that you have done the following:

* Documented changes or features in README.md
* Added appropriate license headers to new files
* Written or modified tests for new functionality
* Formatted code following project standards
* Validated code and formatting with `make test lint`

[black]: https://github.com/psf/black
[isort]: https://timothycrosley.github.io/isort/
[pyenv]: https://github.com/pyenv/pyenv
