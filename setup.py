#!/usr/bin/env python

"""File setup.py
Copyright 2012-2021 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable package.

Orange3-Textable is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3-Textable is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange3-Textable. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

from os import path, walk
import sys

if sys.version_info < (3, ):
    raise RuntimeError("Orange3-Textable requires Python 3")

from setuptools import setup, find_packages

__version__ = "1.0.36"   # file version

NAME = 'Orange3-Textable'
DOCUMENTATION_NAME = 'Textable'

VERSION = '3.1.10'  # package version

DESCRIPTION = 'Textable add-on for Orange 3 data mining software package.'
LONG_DESCRIPTION = open(
    path.join(path.dirname(__file__), 'README.rst')
).read()
AUTHOR = 'LangTech Sarl'
AUTHOR_EMAIL = 'info@langtech.ch'
URL = 'http://textable.io'
DOWNLOAD_URL = 'https://github.com/axanthos/orange3-textable/archive/master.zip'
LICENSE = 'GPLv3'

KEYWORDS = (
    'text mining',
    'text analysis',
    'textable',
    'orange3',
    'orange3 add-on',
)

CLASSIFIERS = (
    'Development Status :: 5 - Production/Stable',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3 :: Only',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Linguistic',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
)

PACKAGES = find_packages(
)

PACKAGE_DATA = {
}

INSTALL_REQUIRES = (
    'Orange3 >= 3.14.0',
    'setuptools',
    'future',
    'LTTL >= 2.0.12',
    'chardet',
    'treetaggerwrapper',
    'appdirs',
    'pycountry',
),

EXTRAS_REQUIRE = {
}

DATA_FILES = list()

DEPENDENCY_LINKS = (
)

ENTRY_POINTS = {
    'orange.addons': (
        'tt = _textable',
    ),
    'orange.widgets': (
        'Textable = _textable.widgets',
    ),
    "orange.canvas.help": (
        'html-index = _textable.widgets:WIDGET_HELP_PATH',
    ),
}

def include_documentation(local_dir, install_dir):
    global DATA_FILES
    if 'bdist_wheel' in sys.argv and not path.exists(local_dir):
        print("Directory '{}' does not exist. "
              "Please build documentation before running bdist_wheel."
              .format(path.abspath(local_dir)))
        sys.exit(0)

    doc_files = []
    for dirpath, dirs, files in walk(local_dir):
        doc_files.append((dirpath.replace(local_dir, install_dir),
                          [path.join(dirpath, f) for f in files]))
    DATA_FILES.extend(doc_files)

    
if __name__ == '__main__':
    include_documentation('docs/doc/_build/', 'help/orange3-textable')
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        dependency_links=DEPENDENCY_LINKS,
        entry_points=ENTRY_POINTS,
        include_package_data=True,
        zip_safe=False,
    )


