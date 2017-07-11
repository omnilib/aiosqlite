# Copyright 2017 John Reese
# Licensed under the MIT license

import asyncio
import logging
import sqlite3

from functools import partial
from queue import Queue, Empty
from threading import Thread
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


class Connection(Thread):
    def __init__(
        self,
        connector: Callable[[], sqlite3.Connection],
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        super().__init__()

        self._running = True
        self._conn = None  # type: sqlite3.Connection
        self._connector = connector
        self._loop = loop
        self._lock = asyncio.Lock(loop=loop)
        self._tx = Queue()
        self._rx = Queue()

    def run(self) -> None:
        """Execute function calls on a separate thread."""
        while self._running:
            try:
                fn = self._tx.get(timeout=0.1)
            except Empty:
                continue

            try:
                Log.debug(f'executing {fn}')
                result = fn()
                Log.debug(f'returning {result}')
                self._rx.put(result)
            except Exception as e:
                Log.debug(f'returning exception {e}')
                self._rx.put(e)

    async def _execute(self, fn, *args, **kwargs):
        """Queue a function with the given arguments for execution."""
        await self._lock.acquire()

        pt = partial(fn, *args, **kwargs)
        self._tx.put_nowait(pt)

        while True:
            try:
                result = self._rx.get_nowait()
                break

            except Empty:
                await asyncio.sleep(0.1)
                continue

        self._lock.release()

        if isinstance(result, Exception):
            raise result

        return result

    async def _connect(self):
        """Connect to the actual sqlite database."""
        if self._conn is None:
            self._conn = await self._execute(self._connector)

    async def __aenter__(self) -> 'Connection':
        self.start()
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
        self._running = False
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

    def connector() -> sqlite3.Connection:
        return sqlite3.connect(
            database,
            **kwargs,
        )

    return Connection(connector, loop)
