"""
Module TestSegment.py, v0.01
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

from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input


class TestSegment(unittest.TestCase):
    """Test suite for LTTL Segment module"""

    def setUp(self):
        """ Setting up for the test """
        self.entire_text_seg = Input(u'ab cde')
        self.other_entire_text_seg = Input(u'd')
        str_index = self.entire_text_seg[0].str_index
        self.first_word_seg = Segmentation(
            [
                Segment(
                        str_index=str_index,
                        start=0,
                        end=2,
                        annotations={u'a': 1}
                )
            ]
        )
        self.last_word_seg = Segmentation(
            [Segment(str_index=str_index, start=3, end=6)]
        )
        self.char_seg = Segmentation(
            [
                Segment(str_index=str_index, start=0, end=1),
                Segment(str_index=str_index, start=1, end=2),
                Segment(str_index=str_index, start=2, end=3),
                Segment(str_index=str_index, start=3, end=4),
                Segment(str_index=str_index, start=4, end=5),
                Segment(str_index=str_index, start=5, end=6),
            ]
        )

    def tearDown(self):
        """Cleaning up after the test"""
        pass

    def test_creator(self):
        """Does creator return Segment object?"""
        mock_address = 1
        self.assertIsInstance(
            Segment(mock_address),
            Segment,
            msg=u"creator doesn't return Segment object!"
        )

    def test_creator_no_str_index_param(self):
        """Does creator raise an exception when called without int param?"""
        self.assertRaises(
            TypeError,
            Segment,
            msg=u"creator raises no exception when called without int param!"
        )

    def test_creator_no_annotations(self):
        """Does creator initialize param annotations to {} by default?"""
        segment = Segment(0, annotations=None)
        self.assertEqual(
            segment.annotations,
            dict(),
            msg=u"creator doesn't init param annotations to {} by default!"
        )

    def test_get_content_complete_addressing(self):
        """Does get_content() work with complete addressing?"""
        self.assertEqual(
            self.char_seg[0].get_content(),
            u'a',
            msg=u"get_content() doesn't work with complete address as param!"
        )

    def test_get_content_missing_start(self):
        """Does get_content() work with start=None?"""
        segment = Segment(
            str_index=self.entire_text_seg[0].str_index,
            start=None,
            end=4,
        )
        self.assertEqual(
            segment.get_content(),
            u'ab c',
            msg=u"get_content() doesn't work with start=None!"
        )

    def test_get_content_missing_end(self):
        """Does get_content() work with end=None?"""
        segment = Segment(
            str_index=self.entire_text_seg[0].str_index,
            start=0,
            end=None,
        )
        self.assertEqual(
            segment.get_content(),
            u'ab cde',
            msg=u"get_content() doesn't work with end=None!"
        )

    def test_get_content_missing_start_and_end(self):
        """Does get_content() work with start=None and end=None?"""
        segment = Segment(
            str_index=self.entire_text_seg[0].str_index,
            start=None,
            end=None,
        )
        self.assertEqual(
            segment.get_content(),
            u'ab cde',
            msg=u"get_content() doesn't work with start=None and end=None!"
        )

    def test_deepcopy_correct_address(self):
        """Does deepcopy correctly copy segment address?"""
        segment = self.first_word_seg[0].deepcopy()
        self.assertEqual(
            [segment.str_index, segment.start, segment.end],
            [
                self.first_word_seg[0].str_index,
                self.first_word_seg[0].start,
                self.first_word_seg[0].end,
            ],
            msg=u"deepcopy doesn't correctly copy segment address!"
        )

    def test_deepcopy_no_annotations_update(self):
        """Does deepcopy work with annotations=None and update=True?"""
        segment = self.first_word_seg[0].deepcopy(
            annotations=None,
            update=True,
        )
        self.assertEqual(
            segment.annotations,
            self.first_word_seg[0].annotations,
            msg=u"deepcopy doesn't work with annotations=None and update=True!"
        )

    def test_deepcopy_no_annotations_no_update(self):
        """Does deepcopy work with annotations=None and update=False?"""
        segment = self.first_word_seg[0].deepcopy(
            annotations=None,
            update=False,
        )
        self.assertEqual(
            segment.annotations,
            dict(),
            msg=u"deepcopy doesn't work with annotations=None and update=False!"
        )

    def test_deepcopy_annotations_update(self):
        """Does deepcopy work with annotations and update=True?"""
        segment = self.first_word_seg[0].deepcopy(
            annotations={u'b': 1},
            update=True,
        )
        self.assertEqual(
            segment.annotations,
            {u'a': 1, u'b': 1},
            msg=u"deepcopy doesn't work with annotations and update=True!"
        )

    def test_deepcopy_annotations_no_update(self):
        """Does deepcopy work with annotations and update=False?"""
        segment = self.first_word_seg[0].deepcopy(
            annotations={u'b': 1},
            update=False,
        )
        self.assertEqual(
            segment.annotations,
            {'b': 1},
            msg=u"deepcopy doesn't work with annotations and update=False!"
        )

    def test_contains_with_contained(self):
        """Does contains recognize contained segment?"""
        self.assertTrue(
            self.entire_text_seg[0].contains(self.char_seg[0]),
            msg=u"contains doesn't recognize contained segment!"
        )

    def test_contains_with_other_string(self):
        """Does contains reject segment from other string?"""
        self.assertFalse(
            self.entire_text_seg[0].contains(self.other_entire_text_seg[0]),
            msg=u"contains doesn't reject segment from other string!"
        )

    def test_contains_with_segment_starting_before(self):
        """Does contains reject segment starting before?"""
        self.assertFalse(
            self.last_word_seg[0].contains(self.entire_text_seg[0]),
            msg=u"contains doesn't reject segment starting before!"
        )

    def test_contains_with_segment_ending_after(self):
        """Does contains reject segment ending after?"""
        self.assertFalse(
            self.first_word_seg[0].contains(self.entire_text_seg[0]),
            msg=u"contains doesn't reject segment ending after!"
        )

    def test_get_contained_segments(self):
        """Does get_contained_segments return contained segments?"""
        self.assertEqual(
            self.first_word_seg[0].get_contained_segments(
                self.char_seg
            ),
            self.char_seg[0:2],
            msg=u"get_contained_segments doesn't return contained segments!"
        )

    def test_get_contained_segment_indices(self):
        """Does get_contained_segment_indices return correct indices?"""
        self.assertEqual(
            self.first_word_seg[0].get_contained_segment_indices(
                self.char_seg
            ),
            [0, 1],
            msg=u"get_contained_segment_indices doesn't return correct indices!"
        )

    def test_get_contained_sequence_indices(self):
        """Does get_contained_sequence_indices return correct indices?"""
        self.assertEqual(
            self.last_word_seg[0].get_contained_sequence_indices(
                self.char_seg,
                2
            ),
            [3, 4],
            msg=u"get_contained_sequence_indices doesn't return correct indices!"
        )


if __name__ == u'__main__':
    unittest.main()

