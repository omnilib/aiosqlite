# Copyright 2017 John Reese
# Licensed under the MIT license

"""
Core implementation of aiosqlite proxies
"""

import asyncio
import logging
import sqlite3

from functools import partial
from queue import Queue, Empty
from threading import Thread
from typing import Any, Callable, Iterable, Optional, Tuple

from .context import contextmanager

__all__ = ["connect", "Connection", "Cursor"]

LOG = logging.getLogger("aiosqlite")


class Cursor:

    def __init__(self, conn: "Connection", cursor: sqlite3.Cursor) -> None:
        self._conn = conn
        self._cursor = cursor

    def __aiter__(self) -> "Cursor":
        """The cursor proxy is also an async iterator."""
        return self

    async def __anext__(self) -> sqlite3.Row:
        """Use `cursor.fetchone()` to provide an async iterable."""
        row = await self.fetchone()
        if row is None:
            raise StopAsyncIteration

        return row

    async def _execute(self, fn, *args, **kwargs):
        """Execute the given function on the shared connection's thread."""
        return await self._conn._execute(fn, *args, **kwargs)

    async def execute(self, sql: str, parameters: Iterable[Any] = None) -> None:
        """Execute the given query."""
        if parameters is None:
            parameters = []
        await self._execute(self._cursor.execute, sql, parameters)

    async def executemany(self, sql: str, parameters: Iterable[Iterable[Any]]) -> None:
        """Execute the given multiquery."""
        await self._execute(self._cursor.executemany, sql, parameters)

    async def executescript(self, sql_script: str) -> None:
        """Execute a user script."""
        await self._execute(self._cursor.executescript, sql_script)

    async def fetchone(self) -> Optional[sqlite3.Row]:
        """Fetch a single row."""
        return await self._execute(self._cursor.fetchone)

    async def fetchmany(self, size: int = None) -> Iterable[sqlite3.Row]:
        """Fetch up to `cursor.arraysize` number of rows."""
        args = ()  # type: Tuple[int, ...]
        if size is not None:
            args = (size,)
        return await self._execute(self._cursor.fetchmany, *args)

    async def fetchall(self) -> Iterable[sqlite3.Row]:
        """Fetch all remaining rows."""
        return await self._execute(self._cursor.fetchall)

    async def close(self) -> None:
        """Close the cursor."""
        await self._execute(self._cursor.close)

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def lastrowid(self) -> int:
        return self._cursor.lastrowid

    @property
    def arraysize(self) -> int:
        return self._cursor.arraysize

    @arraysize.setter
    def arraysize(self, value: int) -> None:
        self._cursor.arraysize = value

    @property
    def description(self) -> Tuple[Tuple]:
        return self._cursor.description

    @property
    def connection(self) -> sqlite3.Connection:
        return self._cursor.connection

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


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
        self._tx = Queue()  # type: Queue
        self._rx = Queue()  # type: Queue

    def run(self) -> None:
        """Execute function calls on a separate thread."""
        while self._running:
            try:
                fn = self._tx.get(timeout=0.1)
            except Empty:
                continue

            try:
                LOG.debug("executing %s", fn)
                result = fn()
                LOG.debug("returning %s", result)
                self._rx.put(result)
            except BaseException as e:
                LOG.exception("returning exception %s", e)
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
                await asyncio.sleep(0.005)
                continue

        self._lock.release()
        if isinstance(result, Exception):
            raise result

        return result

    async def _connect(self):
        """Connect to the actual sqlite database."""
        if self._conn is None:
            self._conn = await self._execute(self._connector)

    async def __aenter__(self) -> "Connection":
        self.start()
        await self._connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
        self._conn = None

    @contextmanager
    async def cursor(self) -> Cursor:
        """Create an aiosqlite cursor wrapping a sqlite3 cursor object."""
        return Cursor(self, await self._execute(self._conn.cursor))

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self._execute(self._conn.commit)

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        await self._execute(self._conn.rollback)

    async def close(self) -> None:
        """Complete queued queries/cursors and close the connection."""
        await self._execute(self._conn.close)
        self._running = False

    @contextmanager
    async def execute(self, sql: str, parameters: Iterable[Any] = None) -> Cursor:
        """Helper to create a cursor and execute the given query."""
        if parameters is None:
            parameters = []
        cursor = await self._execute(self._conn.execute, sql, parameters)
        return Cursor(self, cursor)

    @contextmanager
    async def executemany(
        self, sql: str, parameters: Iterable[Iterable[Any]]
    ) -> Cursor:
        """Helper to create a cursor and execute the given multiquery."""
        cursor = await self._execute(self._conn.executemany, sql, parameters)
        return Cursor(self, cursor)

    @contextmanager
    async def executescript(self, sql_script: str) -> Cursor:
        """Helper to create a cursor and execute a user script."""
        cursor = await self._execute(self._conn.executescript, sql_script)
        return Cursor(self, cursor)

    async def interrupt(self) -> None:
        """Interrupt pending queries."""
        return self._conn.interrupt()

    @property
    def isolation_level(self) -> str:
        return self._conn.isolation_level

    @isolation_level.setter
    def isolation_level(self, value: str) -> None:
        self._conn.isolation_level = value

    @property
    def in_transaction(self) -> bool:
        return self._conn.in_transaction


def connect(database: str, **kwargs: Any) -> Connection:
    """Create and return a connection proxy to the sqlite database."""
    loop = asyncio.get_event_loop()

    def connector() -> sqlite3.Connection:
        return sqlite3.connect(database, **kwargs)

    return Connection(connector, loop)
