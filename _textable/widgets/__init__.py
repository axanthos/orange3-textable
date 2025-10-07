"""File __init__.py
Copyright 2012-2025 Aris Xanthos
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

"""
Textable
========

"""

import sysconfig

NAME = "Textable"

DESCRIPTION = """Add-on for text analysis"""

LONG_DESCRIPTION = """
This extension contains widgets for building data tables based on
heterogeneous text sources, using such operations as segmentation and
annotation.
"""

ICON = "icons/Category-Textable.png"

BACKGROUND = "#90c0ed"

WIDGET_HELP_PATH = (
    # Development documentation
    # You need to build help pages manually using
    # make htmlhelp
    # inside doc folder
    ("{DEVELOP_ROOT}/docs/doc/_build/reference.html", None),

    # Documentation included in wheel
    # Correct DATA_FILES entry is needed in setup.py and documentation has to be built
    # before the wheel is created.
    ("{}/help/orange3-textable/reference.html".format(sysconfig.get_path("data")), None),

    # Online documentation url, used when the local documentation is not available.
    # Url should point to a page with a section Widgets. This section should
    # includes links to documentation pages of each widget. Matching is
    # performed by comparing link caption to widget name.
    ("http://orange3-textable.readthedocs.io/en/latest/reference.html", "")
)