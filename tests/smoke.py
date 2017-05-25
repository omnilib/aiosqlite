# Copyright 2017 John Reese
# Licensed under the MIT license

import aiosqlite
import asyncio
import logging
import sys
import traceback


async def test_connection():
    async with aiosqlite.connect('test.db') as db:
        assert isinstance(db, aiosqlite.Connection)


def setup_logger():
    log = logging.getLogger('')
    log.setLevel(logging.INFO)

    logging.addLevelName(logging.ERROR, 'E')
    logging.addLevelName(logging.WARNING, 'W')
    logging.addLevelName(logging.INFO, 'I')
    logging.addLevelName(logging.DEBUG, 'V')

    date_fmt = r'%H:%M:%S'
    verbose_fmt = ('%(asctime)s,%(msecs)d %(levelname)s '
                   '%(module)s:%(funcName)s():%(lineno)d   '
                   '%(message)s')

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(verbose_fmt, date_fmt))
    log.addHandler(handler)

    return log


def run_tests():
    """Find and execute smoke tests."""
    setup_logger()

    result = 0
    tests = [
        g for g in globals().values()
        if callable(g) and g.__name__.startswith('test_')
    ]

    success = []
    failure = []
    loop = asyncio.get_event_loop()

    for test in tests:
        print('Running smoke test "{0}" ...'.format(test.__name__))
        try:
            loop.run_until_complete(test())
            success.append(test)
        except BaseException:
            result = 1
            failure.append((test, traceback.format_exc()))

    loop.close()

    for test, tb in failure:
        print('=== {} failed ==='.format(test.__name__))
        print(tb)

    print('{}/{} smoke tests passed'.format(len(success), len(tests)))
    sys.exit(result)


if __name__ == '__main__':
    run_tests()
