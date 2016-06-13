"""
Module LTTL.Input, v0.10
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the LTTL package v1.6.

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

from __future__ import absolute_import
from __future__ import unicode_literals


from .Segmentation import Segmentation

from array import array
import numpy as np

MAX_TEXT_BEFORE_COMPRESS = 5 * 10 ** 12


class Input(Segmentation):
    """A class for representing a segmentation which imports a new string in
    the system.
    """

    def __init__(self, text=None, label='input_string', compressed=None):
        """Initialize an Input instance"""
        from .Segment import Segment
        Segmentation.data.append(None)
        str_index = len(Segmentation.data) - 1

        Segmentation.__init__(self)
        self.append(Segment(str_index))
        self.update(text, label, compressed)

    def update(self, text=None, label=None, compressed=None):
        """Set text and label values associated with an Input

        :param text: the string to be imported and associated with this Input

        :param label: the arbitrary label assigned to this Input
        """

        if compressed is None and text is not None:
            compressed = len(text) > MAX_TEXT_BEFORE_COMPRESS
        if compressed:
            Segmentation.data[self[0].str_index] = None if text is None else CompressedString(text)
        else:
            Segmentation.data[self[0].str_index] = text
        self.label = label

    def clear(self):
        """Reset text and label values associated with an Input to None"""
        self.update()


class CompressedString():
    """Compressing string by re-mapping the characters to an 8bit range.
    If more than 256 unique characaters are used in the same text, mapping to 16bits"""
    def __init__(self, text=None):
        if text:
            alphabet = set(text)
            self.char_to_int = {}
            self.int_to_char = []
            index = 0
            self.size = len(text)
            for letter in alphabet:
                self.char_to_int[letter] = index
                self.int_to_char.append(letter)
                index += 1
            if len(alphabet) < 256:
                self.tab = np.empty(len(text), dtype=np.uint8)
            else:
                self.tab = np.empty(len(text), dtype=np.uint16)
            for index, letter in enumerate(text):
                self.tab[index] = self.char_to_int[letter]

    def __len__(self):
        """Return the number of char in string"""
        return self.size

    def __getitem__(self, index):
        """Return the letter of an index"""
        return self.int_to_char[self.tab[index]]

    def __iter__(self):
        """Return an iterator on letter"""
        for letter in self.tab:
            yield self.int_to_char[letter]

    def __getslice__(self, i, j):
        """Return a slice of the string as another CompressedString with a view on this one"""
        sub_string = CompressedString()
        sub_string.int_to_char = self.int_to_char
        sub_string.tab = self.tab[i:j]
        sub_string.size = j - i
        return array('u', sub_string).tounicode()

    def __repr__(self):
        return array('u', self).tounicode()
