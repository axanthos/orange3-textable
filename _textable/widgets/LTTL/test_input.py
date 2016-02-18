"""
Module TestInput.py, v0.01
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the LTTL package v1.6

LTTL v1.6 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LTTL v1.6 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LTTL v1.6. If not, see <http://www.gnu.org/licenses/>.
"""

import unittest

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from LTTL.Segmentation import Segmentation
from LTTL.Input import Input


class TestInput(unittest.TestCase):
    """Test suite for LTTL Segment module"""

    def setUp(self):
        """ Setting up for the test """
        pass

    def tearDown(self):
        """Cleaning up after the test"""
        pass

    def test_creator(self):
        """Does creator return Input object?"""
        self.assertIsInstance(
            Input(),
            Input,
            msg=u"creator doesn't return Input object!"
        )

    def test_creator_store_string(self):
        """Does creator store string in class variable?"""
        Input(u'test')
        self.assertEqual(
            Segmentation.data[-1],
            u'test',
            msg=u"creator doesn't store string in class variable!"
        )

    def test_update_string(self):
        """Does update modify stored string?"""
        seg = Input(u'test2')
        seg.update(u'modified')
        self.assertEqual(
            Segmentation.data[-1],
            u'modified',
            msg=u"update doesn't modify stored string!"
        )

    def test_clear_string(self):
        """Does clear set stored string to None?"""
        seg = Input(u'test3')
        seg.clear()
        self.assertEqual(
            Segmentation.data[-1],
            None,
            msg=u"clear doesn't set stored string to None!"
        )


if __name__ == u'__main__':
    unittest.main()

