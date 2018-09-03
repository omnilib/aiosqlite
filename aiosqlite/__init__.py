# Copyright 2018 John Reese
# Licensed under the MIT license

"""asyncio bridge to sqlite3"""

from sqlite3 import sqlite_version, sqlite_version_info

from .core import connect, Connection, Cursor

__version__ = "0.4.0"
__all__ = [
    "__version__",
    "sqlite_version",
    "sqlite_version_info",
    "connect",
    "Connection",
    "Cursor",
]
