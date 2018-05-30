from setuptools import setup, find_packages
from codecs import open
from os import path
from pracpred import (
    __version__,
    __url__,
    __author__,
    __author_email__,
    __license__,
    __status__,
)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get version and other info from __init__.py
# For old-style VERSION.txt, use:
# with open(path.join(here, 'VERSION.txt')) as version_file:
#    version = version_file.read().strip()
version = __version__
NAME = 'pracpred'
DESCRIPTION = 'Shared code used on practicallypredictable.com.'
URL = __url__
AUTHOR = __author__
EMAIL = __author_email__
LICENSE = 'MIT'  # Make sure consistent with trove classifiers below

REQUIRED = [
    'numpy',
]

setup(
    name=NAME,
    version=version,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=['setuptools>=38.6.0'],
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=REQUIRED,
    include_package_data=True,
    license=LICENSE,
    keywords='probability statistics sports analytics board games',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        __status__,
        __license__,
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
