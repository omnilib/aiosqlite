# Copyright 2017 John Reese
# Licensed under the MIT license

import asyncio
import logging
import sqlite3

from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable, Iterable

__all__ = [
    'connect',
    'Connection',
    'Cursor',
]

Log = logging.getLogger('aiosqlite')


class Cursor:
    def __init__(
        self,
        conn: 'Connection',
        cursor: sqlite3.Cursor,
    ) -> None:
        self._conn = conn
        self._cursor = cursor


class Connection:
    def __init__(
        self,
        connector: Callable[[], sqlite3.Connection],
        loop: asyncio.AbstractEventLoop,
        executor: ThreadPoolExecutor,
    ) -> None:
        self._conn = None  # type: sqlite3.Connection
        self._connector = connector
        self._loop = loop
        self._executor = executor

    async def _execute(self, fn, *args, **kwargs):
        """Execute a function with the given arguments on the shared thread."""
        pt = partial(fn, *args, **kwargs)
        return await self._loop.run_in_executor(self._executor, pt)

    async def _connect(self):
        """Connect to the actual sqlite database."""
        if self._conn is None:
            self._conn = await self._execute(self._connector)

    async def __aenter__(self) -> 'Connection':
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
        self._conn = None

    async def cursor(self) -> Cursor:
        raise NotImplementedError('Not yet available in aiosqlite')

    async def commit(self) -> None:
        raise NotImplementedError('Not yet available in aiosqlite')

    async def rollback(self) -> None:
        raise NotImplementedError('Not yet available in aiosqlite')

    async def close(self) -> None:
        await self._execute(self._conn.close)

    async def execute(
        self,
        sql: str,
        parameters: Iterable[Any] = None,
    ) -> Cursor:
        raise NotImplementedError('Not yet available in aiosqlite')

    async def executemany(
        self,
        sql: str,
        parameters: Iterable[Iterable[Any]] = None,
    ) -> Cursor:
        raise NotImplementedError('Not yet available in aiosqlite')

    async def executescript(
        self,
        sql_script: str,
    ) -> Cursor:
        raise NotImplementedError('Not yet available in aiosqlite')


def connect(
    database: str,
    **kwargs: Any
) -> Connection:
    """Create and return a connection proxy to the sqlite database."""

    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(1)

    def connector() -> sqlite3.Connection:
        return sqlite3.connect(
            database,
            check_same_thread=False,
            **kwargs,
        )

    return Connection(connector, loop, executor)
