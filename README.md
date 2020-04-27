aiosqlite
=========

AsyncIO bridge to the standard `sqlite3` module for Python 3.5+

[![pypi release](https://img.shields.io/pypi/v/aiosqlite.svg)](https://pypi.org/project/aiosqlite)
[![documentation status](https://readthedocs.org/projects/aiosqlite/badge/?version=latest)](https://aiosqlite.omnilib.dev/en/latest/?badge=latest)
[![changelog](https://img.shields.io/badge/change-log-blue)](https://github.com/jreese/aiosqlite/blob/master/CHANGELOG.md)
[![code coverage](https://img.shields.io/codecov/c/github/jreese/aiosqlite/master.svg)](https://codecov.io/gh/jreese/aiosqlite)
[![build status](https://github.com/jreese/aiosqlite/workflows/Build/badge.svg)](https://github.com/jreese/aiosqlite/actions)
[![MIT license](https://img.shields.io/pypi/l/aiosqlite.svg)](https://github.com/jreese/aiosqlite/blob/master/LICENSE)
[![code style black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


Install
-------

aiosqlite is compatible with Python 3.5 and newer.
You can install it from PyPI with the following command:

    $ pip install aiosqlite


Overview
--------

aiosqlite replicates the standard `sqlite3` module, but with async versions
of all the standard connection and cursor methods, and context managers for
automatically closing connections:

```python
    async with aiosqlite.connect(...) as db:
        await db.execute('INSERT INTO some_table ...')
        await db.commit()

        async with db.execute('SELECT * FROM some_table') as cursor:
            async for row in cursor:
                ...
```

Full documentation is available [on Omnilib.dev](https://aiosqlite.omnilib.dev).


License
-------

aiosqlite is copyright [John Reese](https://jreese.sh), and licensed under the
MIT license.  I am providing code in this repository to you under an open source
license.  This is my personal repository; the license you receive to my code
is from me and not from my employer. See the `LICENSE` file for details.
