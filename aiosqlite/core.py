# Copyright 2018 John Reese
# Licensed under the MIT license

"""
Core implementation of aiosqlite proxies
"""

import asyncio
import logging
import sqlite3

from functools import partial
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from typing import Any, Callable, Generator, Iterable, Optional, Tuple, Type, Union

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
        self._connection = None  # type: Optional[sqlite3.Connection]
        self._connector = connector
        self._loop = loop
        self._tx = Queue()  # type: Queue

    @property
    def _conn(self) -> sqlite3.Connection:
        if self._connection is None:
            raise ValueError("no active connection")

        return self._connection

    def _execute_insert(
        self, sql: str, parameters: Iterable[Any]
    ) -> Optional[sqlite3.Row]:
        cursor = self._conn.execute(sql, parameters)
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()

    def _execute_fetchall(
        self, sql: str, parameters: Iterable[Any]
    ) -> Iterable[sqlite3.Row]:
        cursor = self._conn.execute(sql, parameters)
        return cursor.fetchall()

    def run(self) -> None:
        """Execute function calls on a separate thread."""
        while self._running:
            try:
                future, function = self._tx.get(timeout=0.1)
            except Empty:
                continue

            try:
                LOG.debug("executing %s", function)
                result = function()
                LOG.debug("returning %s", result)
                self._loop.call_soon_threadsafe(future.set_result, result)
            except BaseException as e:
                LOG.exception("returning exception %s", e)
                self._loop.call_soon_threadsafe(future.set_exception, e)

    async def _execute(self, fn, *args, **kwargs):
        """Queue a function with the given arguments for execution."""
        function = partial(fn, *args, **kwargs)
        future = self._loop.create_future()

        self._tx.put_nowait((future, function))

        return await future

    async def _connect(self) -> "Connection":
        """Connect to the actual sqlite database."""
        if self._connection is None:
            self._connection = await self._execute(self._connector)
        return self

    def __await__(self) -> Generator[Any, None, "Connection"]:
        self.start()
        return self._connect().__await__()

    async def __aenter__(self) -> "Connection":
        return await self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

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
        self._connection = None

    @contextmanager
    async def execute(self, sql: str, parameters: Iterable[Any] = None) -> Cursor:
        """Helper to create a cursor and execute the given query."""
        if parameters is None:
            parameters = []
        cursor = await self._execute(self._conn.execute, sql, parameters)
        return Cursor(self, cursor)

    @contextmanager
    async def execute_insert(
        self, sql: str, parameters: Iterable[Any] = None
    ) -> Optional[sqlite3.Row]:
        """Helper to insert and get the last_insert_rowid."""
        if parameters is None:
            parameters = []
        return await self._execute(self._execute_insert, sql, parameters)

    @contextmanager
    async def execute_fetchall(
        self, sql: str, parameters: Iterable[Any] = None
    ) -> Iterable[sqlite3.Row]:
        """Helper to execute a query and return all the data."""
        if parameters is None:
            parameters = []
        return await self._execute(self._execute_fetchall, sql, parameters)

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

    async def create_function(self, name: str, num_params: int, func: Callable) -> None:
        """Create user-defined function that can be later used
        within SQL statements. Must be run within the same thread
        that query executions take place so instead of executing directly
        against the connection, we defer this to `run` function."""
        await self._execute(self._conn.create_function, name, num_params, func)

    @property
    def in_transaction(self) -> bool:
        return self._conn.in_transaction

    @property
    def isolation_level(self) -> str:
        return self._conn.isolation_level

    @isolation_level.setter
    def isolation_level(self, value: str) -> None:
        self._conn.isolation_level = value

    @property
    def row_factory(self) -> "Optional[Type]":  # py3.5.2 compat (#24)
        return self._conn.row_factory

    @row_factory.setter
    def row_factory(self, factory: "Optional[Type]") -> None:  # py3.5.2 compat (#24)
        self._conn.row_factory = factory

    @property
    def text_factory(self) -> Type:
        return self._conn.text_factory

    @text_factory.setter
    def text_factory(self, factory: Type) -> None:
        self._conn.text_factory = factory

    @property
    def total_changes(self) -> int:
        return self._conn.total_changes

    async def enable_load_extension(self, value: bool) -> None:
        await self._execute(self._conn.enable_load_extension, value)  # type: ignore

    async def load_extension(self, path: str):
        await self._execute(self._conn.load_extension, path)  # type: ignore

    async def set_progress_handler(
        self, handler: Callable[[], Optional[int]], n: int
    ) -> None:
        await self._execute(self._conn.set_progress_handler, handler, n)


def connect(
    database: Union[str, Path], *, loop: asyncio.AbstractEventLoop = None, **kwargs: Any
) -> Connection:
    """Create and return a connection proxy to the sqlite database."""
    if loop is None:
        loop = asyncio.get_event_loop()

    def connector() -> sqlite3.Connection:
        if isinstance(database, str):
            loc = database
        elif isinstance(database, bytes):
            loc = database.decode("utf-8")
        else:
            loc = str(database)

        return sqlite3.connect(loc, **kwargs)

    return Connection(connector, loop)
