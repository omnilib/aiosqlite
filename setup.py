from setuptools import setup

from os import path
import shutil

if path.isfile('README.rst'):
    shutil.copyfile('README.rst', 'README')

setup(
    name='aiosqlite',
    description='asyncio bridge to the standard sqlite3 module',
    version='0.2.0',
    author='John Reese',
    author_email='john@noswap.com',
    url='https://github.com/jreese/aiosqlite',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
    license='MIT License',
    packages=['aiosqlite'],
    install_requires=[
    ],
)
