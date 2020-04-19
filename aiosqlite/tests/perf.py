# Copyright 2018 John Reese
# Licensed under the MIT license

"""
Simple perf tests for aiosqlite and the asyncio run loop.
"""

import time
from pathlib import Path

import aiounittest

import aiosqlite

from .smoke import setup_logger

TEST_DB = Path(":memory:")
TARGET = 2.0
RESULTS = {}


def timed(fn):
    """
    Decorator for perf testing a block of async code.

    Expects the wrapped function to return an async generator.
    The generator should do setup, then yield when ready to start perf testing.
    The decorator will then pump the generator repeatedly until the target
    time has been reached, then close the generator and print perf results.
    """

    name = fn.__name__

    async def wrapper(*args, **kwargs):
        gen = fn(*args, **kwargs)

        await gen.asend(None)
        count = 0
        before = time.time()

        while True:
            count += 1
            value = time.time() - before < TARGET
            try:
                if value:
                    await gen.asend(value)
                else:
                    await gen.aclose()
                    break

            except StopAsyncIteration:
                break

            except Exception as e:
                print(f"exception occurred: {e}")
                return

        duration = time.time() - before

        RESULTS[name] = (count, duration)

    return wrapper


class PerfTest(aiounittest.AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        print(f"Running perf tests for at least {TARGET:.1f}s each...")
        setup_logger()

    @classmethod
    def tearDownClass(cls):
        print(f"\n{'Perf Test':<25} Iterations  Duration  {'Rate':>11}")
        for name in sorted(RESULTS):
            count, duration = RESULTS[name]
            rate = count / duration
            name = name.replace("test_", "")
            print(f"{name:<25} {count:>10}  {duration:>7.1f}s  {rate:>9.1f}/s")

    def setUp(self):
        if TEST_DB.exists():
            TEST_DB.unlink()

    @timed
    async def test_atomics(self):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("create table perf (i integer primary key asc, k integer)")
            await db.execute("insert into perf (k) values (2), (3)")
            await db.commit()

            while True:
                yield
                async with db.execute("select last_insert_rowid()") as cursor:
                    _row_id = await cursor.fetchone()

    @timed
    async def test_inserts(self):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("create table perf (i integer primary key asc, k integer)")
            await db.commit()

            while True:
                yield
                await db.execute("insert into perf (k) values (1), (2), (3)")
                await db.commit()

    @timed
    async def test_insert_ids(self):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("create table perf (i integer primary key asc, k integer)")
            await db.commit()

            while True:
                yield
                cursor = await db.execute("insert into perf (k) values (1)")
                await cursor.execute("select last_insert_rowid()")
                await cursor.fetchone()
                await db.commit()

    @timed
    async def test_insert_macro_ids(self):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("create table perf (i integer primary key asc, k integer)")
            await db.commit()

            while True:
                yield
                await db.execute_insert("insert into perf (k) values (1)")
                await db.commit()

    @timed
    async def test_select(self):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("create table perf (i integer primary key asc, k integer)")
            for i in range(100):
                await db.execute("insert into perf (k) values (%d)" % (i,))
            await db.commit()

            while True:
                yield
                cursor = await db.execute("select i, k from perf")
                assert len(await cursor.fetchall()) == 100

    @timed
    async def test_select_macro(self):
        async with aiosqlite.connect(TEST_DB) as db:
            await db.execute("create table perf (i integer primary key asc, k integer)")
            for i in range(100):
                await db.execute("insert into perf (k) values (%d)" % (i,))
            await db.commit()

            while True:
                yield
                assert len(await db.execute_fetchall("select i, k from perf")) == 100
