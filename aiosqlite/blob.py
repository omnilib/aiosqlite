# Copyright Amethyst Reese
# Licensed under the MIT license

from __future__ import annotations

import os
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Connection


class Blob:
    """Proxy for a ``sqlite3.Blob``, running all operations on the shared thread.

    Instances are created by :meth:`Connection.blobopen`, and are best used as an
    async context manager so the blob is closed automatically::

        async with db.blobopen("table", "column", row_id) as blob:
            await blob.write(b"hello")

    """

    # `blob` is a sqlite3.Blob, but that type only exists on Python 3.11+ while
    # the type checker targets 3.9, so it's left untyped here.
    def __init__(self, conn: "Connection", blob: Any) -> None:
        self._conn = conn
        self._blob = blob

    async def _execute(self, fn, *args, **kwargs):
        """Execute the given function on the shared connection's thread."""
        return await self._conn._execute(fn, *args, **kwargs)

    async def read(self, length: int = -1) -> bytes:
        """Read `length` bytes of data, or to the end of the blob if negative."""
        return await self._execute(self._blob.read, length)

    async def write(self, data: bytes) -> None:
        """Write `data` to the blob at the current offset."""
        await self._execute(self._blob.write, data)

    async def tell(self) -> int:
        """Return the current access position of the blob."""
        return await self._execute(self._blob.tell)

    async def seek(self, offset: int, origin: int = os.SEEK_SET) -> None:
        """Set the access position of the blob to `offset`, relative to `origin`."""
        await self._execute(self._blob.seek, offset, origin)

    async def length(self) -> int:
        """Return the size of the blob in bytes."""
        return await self._execute(len, self._blob)

    async def close(self) -> None:
        """Close the blob."""
        await self._execute(self._blob.close)

    async def __aenter__(self) -> "Blob":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
