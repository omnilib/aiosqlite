# Copyright Amethyst Reese
# Licensed under the MIT license
# mypy: warn-unused-ignores

import sqlite3
from collections.abc import Iterable
from typing import Optional

from aiosqlite import Connection, Cursor


# Checked by mypy; the runtime test suite never calls this function.
async def check_connection_signatures(db: Connection, cursor: Cursor) -> None:
    result: Cursor = await db.cursor()
    result = await db.execute(sql="SELECT ?", parameters=(1,))
    result = await db.executemany(sql="INSERT INTO items VALUES (?)", parameters=[(1,)])
    result = await db.executescript(sql_script="SELECT 1;")
    inserted: Optional[sqlite3.Row] = await db.execute_insert(
        "INSERT INTO items VALUES (?)", (1,)
    )
    rows: Iterable[sqlite3.Row] = await db.execute_fetchall("SELECT 1")
    result = await Connection.execute(db, "SELECT 1")
    async with db.cursor() as managed_cursor:
        result = managed_cursor
    async with db.execute("SELECT 1") as managed_execute:
        result = managed_execute
    _ = result, inserted, rows
    await db.execute(42)  # type: ignore[arg-type]
    await db.executescript(42)  # type: ignore[arg-type]
    await db.execute_insert(42)  # type: ignore[arg-type]
    await db.execute_fetchall(42)  # type: ignore[arg-type]
    await db.execute("SELECT ?", object())  # type: ignore[arg-type]
    await db.execute()  # type: ignore[call-arg]
    await db.executemany("INSERT INTO items VALUES (?)")  # type: ignore[call-arg]
    await db.cursor(1)  # type: ignore[call-arg]
    await db.execute(statement="SELECT 1")  # type: ignore[call-arg]
    await db.executescript(script="SELECT 1;")  # type: ignore[call-arg]
    await Connection.execute(object(), "SELECT 1")  # type: ignore[arg-type]
    await cursor.execute(42)  # type: ignore[arg-type]
