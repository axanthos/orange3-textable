#!/usr/bin/env python

#=============================================================================
# File setup.py, v0.10
# Copyright 2012-2014 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the Textable (v1.4) extension to Orange Canvas.
#
# Textable v1.4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Textable v1.4 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Textable v1.4. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

try:
    import distribute_setup
    distribute_setup.use_setuptools()
except ImportError:
    # For documentation we load setup.py to get version
    # so it does not matter if importing fails
    pass

import os

from setuptools import setup, find_packages

NAME = 'Orange-Textable'
DOCUMENTATION_NAME = 'Orange Textable'

VERSION = '1.4.1'

DESCRIPTION = 'Orange Textable add-on for Orange data mining software package.'
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
AUTHOR = 'LangTech Sarl'
AUTHOR_EMAIL = 'info@langtech.ch'
URL = 'http://langtech.ch/textable'
DOWNLOAD_URL = 'https://bitbucket.org/langtech/orange-textable/downloads'
LICENSE = 'GPLv3'

KEYWORDS = (
    'text mining',
    'text analysis',
    'textable',
    'orange',
    'orange add-on',
)

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Plugins',
    'Programming Language :: Python',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Linguistic',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
)

PACKAGES = find_packages(
)

PACKAGE_DATA = {
}

SETUP_REQUIRES = (
    'setuptools',
)

INSTALL_REQUIRES = (
    'Orange',
    'setuptools',
),

EXTRAS_REQUIRE = {
}

DEPENDENCY_LINKS = (
)

ENTRY_POINTS = {
    'orange.addons': (
        'tt = _textable',
    ),
    'orange.widgets': (
        'Textable = _textable.widgets',
    ),
    'orange.canvas.help': (
        'intersphinx = _textable:doc_root'
    ),
}

if __name__ == '__main__':
    setup(
        name = NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        url = URL,
        download_url = DOWNLOAD_URL,
        license = LICENSE,
        keywords = KEYWORDS,
        classifiers = CLASSIFIERS,
        packages = PACKAGES,
        package_data = PACKAGE_DATA,
        setup_requires = SETUP_REQUIRES,
        install_requires = INSTALL_REQUIRES,
        extras_require = EXTRAS_REQUIRE,
        dependency_links = DEPENDENCY_LINKS,
        entry_points = ENTRY_POINTS,
        include_package_data = True,
        zip_safe = False,
    )


