
API Reference
=============

.. module:: aiosqlite

Connection
----------

.. autofunction:: connect

.. autoclass:: Connection
    :special-members: __aenter__, __aexit__, __await__

Cursors
-------

.. autoclass:: aiosqlite.cursor.Cursor
    :special-members: __aiter__, __anext__, __aenter__, __aexit__

Errors
------

.. autoexception:: Warning
    :members:

.. autoexception:: Error
    :members:

.. autoexception:: InterfaceError
    :members:

.. autoexception:: DatabaseError
    :members:

.. autoexception:: DataError
    :members:

.. autoexception:: IntegrityError
    :members:

.. autoexception:: ProgrammingError
    :members:

.. autoexception:: OperationalError
    :members:

.. autoexception:: InternalError
    :members:

.. autoexception:: NotSupportedError
    :members:

Advanced
--------

.. autofunction:: register_adapter

.. autofunction:: register_converter

