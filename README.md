aiosqlite
=========

AsyncIO bridge to the standard `sqlite3` module for Python 3.5+

[![pypi release](https://img.shields.io/pypi/v/aiosqlite.svg)](https://pypi.org/project/aiosqlite)
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


Usage
-----

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

Alternately, you can continue using connections and cursors more procedurally:

```python
    db = await aiosqlite.connect(...)
    cursor = await db.execute('SELECT * FROM some_table')
    row = await cursor.fetchone()
    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
```

aiosqlite also replicates most of the standard connection properties, as needed
for advanced use cases like row or text factories, or for tracking the total
number of rows inserted, modified, or deleted:

```python
    async with aiosqlite.connect(...) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM some_table') as cursor:
            value = row['column']

        await db.execute('INSERT INTO foo some_table')
        assert db.total_changes > 0
```


Details
-------

aiosqlite allows interaction with SQLite databases on the main AsyncIO event
loop without blocking execution of other coroutines while waiting for queries
or data fetches.  It does this by using a single, shared thread per connection.
This thread executes all actions within a shared request queue to prevent
overlapping actions.

Connection objects are proxies to the real connections, contain the shared
execution thread, and provide context managers to handle automatically closing
connections.  Cursors are similarly proxies to the real cursors, and provide
async iterators to query results.


License
-------

aiosqlite is copyright [John Reese](https://jreese.sh), and licensed under the
MIT license.  I am providing code in this repository to you under an open source
license.  This is my personal repository; the license you receive to my code
is from me and not from my employer. See the `LICENSE` file for details.
