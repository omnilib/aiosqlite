# Contributing to aiosqlite

## Preparation

You'll need to have at least Python 3.8 available for testing.

You can do this with [pyenv][]:

    $ pyenv install <version>
    $ pyenv local <version>
    
    
## Setup

Once cloned, create a clean virtual environment and
install the appropriate tools and dependencies:

    $ cd <path/to/aiosqlite>
    $ make venv
    $ source .venv/bin/activate


## Formatting

aiosqlite uses *[ufmt][]* for formatting code and imports.
If your editor does not already support this workflow,
you can manually format files:

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

[pyenv]: https://github.com/pyenv/pyenv
[µfmt]: https://ufmt.omnilib.dev
