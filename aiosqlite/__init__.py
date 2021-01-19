# Copyright 2018 John Reese
# Licensed under the MIT license

"""asyncio bridge to the standard sqlite3 module"""

from sqlite3 import (  # pylint: disable=redefined-builtin
    DatabaseError,
    Error,
    IntegrityError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
    Row,
    Warning,
    register_adapter,
    register_converter,
    sqlite_version,
    sqlite_version_info,
)

__author__ = "John Reese"
from .__version__ import __version__
from .core import Connection, Cursor, connect

__all__ = [
    "__version__",
    "register_adapter",
    "register_converter",
    "sqlite_version",
    "sqlite_version_info",
    "connect",
    "Connection",
    "Cursor",
    "Row",
    "Warning",
    "Error",
    "DatabaseError",
    "IntegrityError",
    "ProgrammingError",
    "OperationalError",
    "NotSupportedError",
]
