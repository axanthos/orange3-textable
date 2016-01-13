"""
=============================================================================
Module TestAddress.py, v0.01
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
=============================================================================
This file is part of the LTTL package v1.5

LTTL v1.5 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

LTTL v1.5 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with LTTL v1.5. If not, see <http://www.gnu.org/licenses/>.
=============================================================================
"""

import unittest

from _textable.widgets.LTTL.Address import Address

class TestAddress(unittest.TestCase):
    """Test suite for LTTL Address module"""

    def setUp(self):
        """ Setting up for the test """
        pass

    def tearDown(self):
        """Cleaning up after the test"""
        pass

    def test_creator(self):
        """Does creator return Address object?"""
        self.assertIsInstance(
            Address(1),
            Address,
            msg="creator doesn't return Address object!"
        )

    def test_creator_no_str_index_param(self):
        """Does creator raise an exception when called without int param?"""
        self.assertRaises(
            TypeError,
            Address,
            msg="creator raises no exception when called without int param!"
        )

if __name__ == '__main__':
    unittest.main()

