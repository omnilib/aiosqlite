# Contributing to aiosqlite

## Preparation

You'll need to have Python 3.5 available for testing.

You can do this with [pyenv][]:

    $ pyenv install 3.5.6
    $ pyenv shell 3.5.6
    
    
## Setup

Once cloned, create a clean virtual environment and
install the appropriate tools and dependencies:

    $ cd <path/to/aiosqlite>
    $ make dev
    $ source .py3/bin/activate


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
* Used [black][] to format code appropriately
* Validated code with `make test lint`

[black]: https://github.com/ambv/black
[pyenv]: https://github.com/pyenv/pyenv
