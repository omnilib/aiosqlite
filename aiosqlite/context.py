# Copyright 2018
# Licensed under the MIT license


from collections.abc import Coroutine
from functools import wraps


class ContextManager(Coroutine):
    __slots__ = ("_coro", "_obj")

    def __init__(self, coro):
        self._coro = coro
        self._obj = None

    def send(self, value):
        return self._coro.send(value)

    def throw(self, typ, val=None, tb=None):
        if val is None:
            return self._coro.throw(typ)

        if tb is None:
            return self._coro.throw(typ, val)

        return self._coro.throw(typ, val, tb)

    def close(self):
        return self._coro.close()

    def __await__(self):
        return self._coro.__await__()

    async def __aenter__(self):
        self._obj = await self._coro
        return self._obj

    async def __aexit__(self, exc_type, exc, tb):
        await self._obj.close()
        self._obj = None


def contextmanager(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> ContextManager:
        return ContextManager(method(self, *args, **kwargs))

    return wrapper
