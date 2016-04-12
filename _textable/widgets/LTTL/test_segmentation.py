"""
Module TestSegmentation.py, v0.01
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

from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input


class TestSegmentation(unittest.TestCase):
    """Test suite for LTTL Segment module"""

    def setUp(self):
        """ Setting up for the test """
        self.entire_text_seg = Input('ab cde')
        self.str_index = self.entire_text_seg[0].str_index
        self.word_seg = Segmentation(
            [
                Segment(
                    str_index=self.str_index,
                    start=0,
                    end=2,
                    annotations={'a': '1', 'bc': '20'}
                ),
                Segment(
                    str_index=self.str_index,
                    start=3,
                    end=6
                )
            ]
        )
        self.overlapping_seg = Segmentation(
            [
                Segment(str_index=self.str_index, start=3, end=5),
                Segment(str_index=self.str_index, start=4, end=6),
            ]
        )

        self.base_output_string = (
            'segment number 1\n'
            '\tcontent:\t"ab"\n'
            '\tstr_index:\t%i\n'
            '\tstart:\t0\n'
            '\tend:\t2\n'
            '\tannotations:\n'
            '\t\ta                    1\n'
            '\t\tbc                   20\n'
            'segment number 2\n'
            '\tcontent:\t"cde"\n'
            '\tstr_index:\t%i\n'
            '\tstart:\t3\n'
            '\tend:\t6'
        ) % (self.str_index, self.str_index)

        self.count = 0

    def tearDown(self):
        """Cleaning up after the test"""
        pass

    def test_creator(self):
        """Does creator return Segmentation object?"""
        self.assertIsInstance(
            Segmentation(),
            Segmentation,
            msg="creator doesn't return Segmentation object!"
        )

    def test_to_string_default_format(self):
        """Does to_string() format segmentation correctly by default?"""
        output_string = self.word_seg.to_string()
        self.assertEqual(
            output_string,
            self.base_output_string,
            msg="to_string() doesn't format segmentation correctly by default!"
        )

    def test_to_string_header(self):
        """Does to_string() format header correctly?"""
        output_string = self.word_seg.to_string(
            header='HEADER',
        )
        self.assertEqual(
            output_string,
            'HEADER' + self.base_output_string,
            msg="to_string() doesn't format header correctly!"
        )

    def test_to_string_footer(self):
        """Does to_string() format footer correctly?"""
        output_string = self.word_seg.to_string(
            footer='FOOTER',
        )
        self.assertEqual(
            output_string,
            self.base_output_string + 'FOOTER',
            msg="to_string() doesn't format footer correctly!"
        )

    def test_to_string_humanize_addresses(self):
        """Does to_string() humanize addresses?"""
        output_string = self.word_seg.to_string(
            humanize_addresses=True,
        )
        humanized_str_index = self.str_index + 1
        humanized_string = self.base_output_string.replace('t:\t3', 't:\t4')
        humanized_string = humanized_string.replace('t:\t0', 't:\t1')
        humanized_string = humanized_string.replace(
            'x:\t%i' % self.str_index,
            'x:\t%i' % humanized_str_index
        )
        self.assertEqual(
            output_string,
            humanized_string,
            msg="to_string() doesn't humanize addresses!"
        )

    def test_to_string_interpolate_builtin_variables(self):
        """Does to_string() interpolate builtin variables?"""
        output_string = self.word_seg.to_string(
            formatting=(
                '%(__num__)s,%(__content__)s,'
                '%(__str_index__)s,%(__start__)s,%(__end__)s,'
                '%(__str_index_raw__)s,%(__start_raw__)s,%(__end_raw__)s'
            )
        )
        self.assertEqual(
            output_string,
            '1,ab,%i,0,2,%i,0,2\n2,cde,%i,3,6,%i,3,6' % (
                self.str_index, self.str_index, self.str_index, self.str_index
            ),
            msg="to_string() doesn't interpolate builtin variables!"
        )

    def test_to_string_interpolate_annotations(self):
        """Does to_string() interpolate annotations?"""
        output_string = self.word_seg.to_string(
            formatting='%(a)s'
        )
        self.assertEqual(
            output_string,
            '1\n__none__',
            msg="to_string() doesn't interpolate annotations!"
        )

    def test_to_string_progress(self):
        """Does to_string track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        self.word_seg.to_string(
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.word_seg),
            msg="to_string doesn't track progress!"
        )

    def test_get_annotation_keys(self):
        """Does get_annotation_keys() return existing annotations?"""
        annotations = self.word_seg.get_annotation_keys()
        self.assertEqual(
            sorted(annotations),
            sorted(['a', 'bc']),
            msg="get_annotation_keys() doesn't return existing annotations!"
        )

    def test_is_non_overlapping(self):
        """Does is_non_overlapping() recognize absence of overlap?"""
        self.assertTrue(
            self.word_seg.is_non_overlapping(),
            msg="is_non_overlapping() doesn't recognize absence of overlap!"
        )

    def test_is_overlapping(self):
        """Does is_non_overlapping() recognize presence of overlap?"""
        self.assertFalse(
            self.overlapping_seg.is_non_overlapping(),
            msg="is_non_overlapping() doesn't recognize presence of overlap!"
        )


if __name__ == '__main__':
    unittest.main()

