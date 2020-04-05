# Copyright 2018 John Reese
# Licensed under the MIT license

"""asyncio bridge to sqlite3"""

from sqlite3 import (  # pylint: disable=redefined-builtin
    register_adapter,
    register_converter,
    sqlite_version,
    sqlite_version_info,
    Row,
    Warning,
    Error,
    DatabaseError,
    IntegrityError,
    ProgrammingError,
    OperationalError,
    NotSupportedError,
)

from .core import connect, Connection, Cursor

__version__ = "0.12.0"
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
