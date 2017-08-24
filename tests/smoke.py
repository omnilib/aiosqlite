# Copyright 2017 John Reese
# Licensed under the MIT license

import aiosqlite
import asyncio
import logging
import os
import sys
import traceback

TEST_DB = 'test.db'


async def test_connection():
    async with aiosqlite.connect(TEST_DB) as db:
        assert isinstance(db, aiosqlite.Connection)


async def test_multiple_connections():
    async with aiosqlite.connect(TEST_DB) as db:
        await db.execute(
            'create table multiple_connections '
            '(i integer primary key asc, k integer)'
        )

    async def do_one_conn(i):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute(
                'insert into multiple_connections (k) values (?)', [i]
            )
            await db.commit()

    await asyncio.gather(*[
        do_one_conn(i) for i in range(10)
    ])

    async with aiosqlite.connect(TEST_DB) as db:
        cursor = await db.execute('select * from multiple_connections')
        rows = await cursor.fetchall()

    assert len(rows) == 10


async def test_multiple_queries():
    async with aiosqlite.connect(TEST_DB) as db:
        await db.execute(
            'create table multiple_queries '
            '(i integer primary key asc, k integer)'
        )

        await asyncio.gather(*[
            db.execute(
                'insert into multiple_queries (k) values (?)', [i]
            ) for i in range(10)
        ])

        await db.commit()

    async with aiosqlite.connect(TEST_DB) as db:
        cursor = await db.execute('select * from multiple_queries')
        rows = await cursor.fetchall()

    assert len(rows) == 10


async def test_iterable_cursor():
    async with aiosqlite.connect(TEST_DB) as db:
        cursor = await db.cursor()
        await cursor.execute(
            'create table iterable_cursor '
            '(i integer primary key asc, k integer)'
        )
        await cursor.executemany(
            'insert into iterable_cursor (k) values (?)',
            [[i] for i in range(10)]
        )
        await db.commit()

    async with aiosqlite.connect(TEST_DB) as db:
        cursor = await db.execute('select * from iterable_cursor')
        rows = []
        async for row in cursor:
            rows.append(row)

    assert len(rows) == 10


def setup_logger():
    log = logging.getLogger('')
    log.setLevel(logging.INFO)

    logging.addLevelName(logging.ERROR, 'E')
    logging.addLevelName(logging.WARNING, 'W')
    logging.addLevelName(logging.INFO, 'I')
    logging.addLevelName(logging.DEBUG, 'V')

    date_fmt = r'%H:%M:%S'
    verbose_fmt = ('%(asctime)s,%(msecs)d %(levelname)s '
                   '%(module)s:%(funcName)s():%(lineno)d   '
                   '%(message)s')

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(verbose_fmt, date_fmt))
    log.addHandler(handler)

    return log


def cleanup():
    if os.path.exists(TEST_DB):
        os.unlink(TEST_DB)


def run_tests():
    """Find and execute smoke tests."""
    setup_logger()
    cleanup()

    result = 0
    tests = [
        g for g in globals().values()
        if callable(g) and g.__name__.startswith('test_')
    ]

    success = []
    failure = []
    loop = asyncio.get_event_loop()

    for test in tests:
        print('Running smoke test "{0}" ...'.format(test.__name__))
        try:
            loop.run_until_complete(test())
            success.append(test)
        except BaseException:
            result = 1
            failure.append((test, traceback.format_exc()))

    loop.close()

    for test, tb in failure:
        print('=== {} failed ==='.format(test.__name__))
        print(tb)

    print('{}/{} smoke tests passed'.format(len(success), len(tests)))
    cleanup()
    sys.exit(result)


if __name__ == '__main__':
    run_tests()
