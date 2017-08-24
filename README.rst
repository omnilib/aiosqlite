aiosqlite
=========

AsyncIO bridge to the standard ``sqlite3`` module for Python 3.5+

.. image:: https://travis-ci.org/jreese/aiosqlite.svg?branch=master
    :target: https://travis-ci.org/jreese/aiosqlite


Install
-------

aiosqlite is compatible with Python 3.5 and newer.
You can install it from PyPI with the following command::

    $ pip install aiosqlite


Usage
-----

aiosqlite replicates the standard ``sqlite3`` module, but with async versions
of all the standard connection and cursor methods, and context managers for
automatically closing connections::

    async with aiosqlite.connect(...) as db:
        await db.execute('INSERT INTO some_table ...')
        await db.commit()

        cursor = await db.execute('SELECT * FROM some_table')

        async for row in cursor:
            ...


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

aiosqlite is copyright John Reese, and licensed under the MIT license.
I am providing code in this repository to you under an open source license.
This is my personal repository; the license you receive to my code
is from me and not from my employer. See the ``LICENSE`` file for details.
