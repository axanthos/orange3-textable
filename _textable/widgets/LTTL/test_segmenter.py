"""
Module TestSegmenter.py, v0.01
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

import re
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from LTTL.Segment import Segment
from LTTL.Segmentation import Segmentation
from LTTL.Input import Input
from LTTL import Segmenter


class TestSegmenter(unittest.TestCase):
    """Test suite for LTTL Segment module"""

    def setUp(self):
        """ Setting up for the test """
        self.entire_text_seg = Input('ab cde')
        str_index = self.entire_text_seg[0].str_index
        self.word_seg = Segmentation(
            [
                Segment(
                    str_index=str_index,
                    start=0,
                    end=2,
                    annotations={'a': '1'}
                ),
                Segment(
                    str_index=str_index,
                    start=3,
                    end=6
                )
            ]
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
        self.letter_seg1 = Segmentation(
            [
                Segment(
                    str_index=str_index,
                    start=0,
                    end=1,
                    annotations={'a': '1'}
                ),
                Segment(str_index=str_index, start=1, end=2),
            ]
        )
        self.letter_seg2 = Segmentation(
            [
                Segment(str_index=str_index, start=3, end=4),
                Segment(
                    str_index=str_index,
                    start=4,
                    end=5,
                    annotations={'b': '2'}
                ),
                Segment(str_index=str_index, start=5, end=6),
            ]
        )
        self.letter_seg = Segmentation(
            [
                Segment(
                    str_index=str_index,
                    start=0,
                    end=1,
                    annotations={'a': '1'}
                ),
                Segment(str_index=str_index, start=1, end=2),
                Segment(str_index=str_index, start=3, end=4),
                Segment(
                    str_index=str_index,
                    start=4,
                    end=5,
                    annotations={'b': '2'}
                ),
                Segment(str_index=str_index, start=5, end=6),
            ]
        )
        self.single_letter_seg = Segmentation(
            [
                Segment(
                    str_index=str_index,
                    start=4,
                    end=5,
                    annotations={'b': '1'}
                ),
            ]
        )
        self.duplicate_seg = Segmentation(
            [
                Segment(str_index=str_index, start=0, end=1),
                Segment(str_index=str_index, start=0, end=1),
            ]
        )
        self.overlapping_seg = Segmentation(
            [
                Segment(str_index=str_index, start=3, end=5),
                Segment(str_index=str_index, start=4, end=6),
            ]
        )

        self.other_entire_text_seg = Input('abbccc')
        str_index2 = self.other_entire_text_seg[0].str_index
        self.other_letter_seg = Segmentation(
            [
                Segment(
                    str_index=str_index2,
                    start=0,
                    end=1,
                    annotations={'a': '1'}
                ),
                Segment(
                    str_index=str_index2,
                    start=1,
                    end=2,
                    annotations={'a': '1'}
                ),
                Segment(
                    str_index=str_index2,
                    start=2,
                    end=3,
                    annotations={'a': '1'}
                ),
                Segment(
                    str_index=str_index2,
                    start=3,
                    end=4,
                    annotations={'a': '2'}
                ),
                Segment(
                    str_index=str_index2,
                    start=4,
                    end=5,
                    annotations={'a': '2'}
                ),
                Segment(
                    str_index=str_index2,
                    start=5,
                    end=6,
                    annotations={'a': '3'}
                ),
            ]
        )

        self.third_entire_text_seg = Input('bd1')
        str_index3 = self.third_entire_text_seg[0].str_index
        self.third_letter_seg = Segmentation(
            [
                Segment(str_index=str_index3, start=0, end=1),
                Segment(
                    str_index=str_index3,
                    start=1,
                    end=2,
                    annotations={'a': '2'}
                ),
                Segment(
                    str_index=str_index3,
                    start=2,
                    end=3,
                    annotations={'a': 'b'}
                ),
            ]
        )

        self.fourth_entire_text_seg = Input('AB cd\xe9')
        str_index = self.fourth_entire_text_seg[0].str_index
        self.second_word_seg = Segmentation(
            [
                Segment(str_index=str_index, start=0, end=2),
                Segment(str_index=str_index, start=3, end=6),
            ]
        )

        self.xml_seg = Input('<a attr="1"><a attr="2">c<a/>d</a></a>')
        self.wrong_xml_seg = Input('<a><a>test</a>')
        self.wrong_xml_seg2 = Input('<a>test</a></a>')

        self.part_xml_seg = Input('<a>1<a>2<a>3</a>4')
        str_index3 = self.part_xml_seg[0].str_index
        self.part_xml_seg2 = Input('</a>5</a>')
        str_index4 = self.part_xml_seg2[0].str_index
        self.broken_xml_seg = Segmentation(
            [
                Segment(str_index=str_index3, annotations={'a': '1'}),
                Segment(str_index=str_index4),
            ]
        )

        self.count = 0

    def tearDown(self):
        """Cleaning up after the test"""
        pass

    def test_concatenate_merge_segments(self):
        """Does concatenate merge input segments?"""
        segmentation = Segmenter.concatenate(
            [
                self.letter_seg2,
                self.letter_seg1,
            ],
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['c', 'd', 'e', 'a', 'b'],
            msg="concatenate doesn't merge input segments!"
        )

    def test_concatenate_copy_annotations(self):
        """Does concatenate copy annotations?"""
        segmentation = Segmenter.concatenate(
            [
                self.letter_seg2,
                self.letter_seg1,
            ],
            copy_annotations=True,
        )
        self.assertEqual(
            [
                segmentation[1].annotations['b'],
                segmentation[3].annotations['a'],
            ],
            ['2', '1'],
            msg="concatenate doesn't copy annotations!"
        )

    def test_concatenate_copy_annotations_false(self):
        """Does concatenate skip copying annotations?"""
        segmentation = Segmenter.concatenate(
            [
                self.letter_seg2,
                self.letter_seg1,
            ],
            copy_annotations=False,
        )
        self.assertFalse(
            'b' in segmentation[1].annotations or
            'a' in segmentation[3].annotations,
            msg="concatenate doesn't skip copying annotations!"
        )

    def test_concatenate_autonumber(self):
        """Does concatenate autonumber input segments?"""
        segmentation = Segmenter.concatenate(
            [
                self.letter_seg2,
                self.letter_seg1,
            ],
            auto_number_as='num',
        )
        self.assertEqual(
            [s.annotations['num'] for s in segmentation],
            list(range(1, 6)),
            msg="concatenate doesn't autonumber input segments!"
        )

    def test_concatenate_sort(self):
        """Does concatenate sort input segments?"""
        segmentation = Segmenter.concatenate(
            [
                self.letter_seg2,
                self.letter_seg1,
            ],
            sort=True,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['a', 'b', 'c', 'd', 'e'],
            msg="concatenate doesn't sort input segments!"
        )

    def test_concatenate_merge_duplicates(self):
        """Does concatenate merge duplicates?"""
        segmentation = Segmenter.concatenate(
            [
                self.letter_seg2,
                self.single_letter_seg,
            ],
            merge_duplicates=True,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['c', 'd', 'e'],
            msg="concatenate doesn't merge duplicates!"
        )

    def test_concatenate_solve_conflicts_merge_duplicates(self):
        """Does concatenate solve conflicts when merging duplicates?"""
        segmentation = Segmenter.concatenate(
            [
                self.letter_seg2,
                self.single_letter_seg,
            ],
            merge_duplicates=True,
        )
        self.assertEqual(
            segmentation[1].annotations['b'],
            '1',
            msg="concatenate doesn't solve conflicts when merging duplicates!"
        )

    def test_concatenate_progress(self):
        """Does concatenate track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.concatenate(
            [self.letter_seg1],
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.letter_seg1),
            msg="concatenate doesn't track progress!"
        )

    def test_tokenize_segment_tokenize(self):
        """Does tokenize tokenize input?"""
        segmentation = Segmenter.tokenize(
            self.entire_text_seg,
            [
                (re.compile(r'\w+'), 'tokenize'),
                (re.compile(r'\w{3,}'), 'tokenize'),
            ],
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ab', 'cde', 'cde'],
            msg="tokenize doesn't tokenize input!"
        )

    def test_tokenize_import_annotations_tokenize(self):
        """Does tokenize import annotations (mode tokenize)?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [(re.compile(r'\w{2}'), 'tokenize')],
            import_annotations=True
        )
        self.assertEqual(
            segmentation[0].annotations['a'],
            '1',
            msg="tokenize doesn't import annotations (mode tokenize)!"
        )

    def test_tokenize_import_annotations_false_tokenize(self):
        """Does tokenize skip importing annotations (mode tokenize)?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [(re.compile(r'\w{2}'), 'tokenize')],
            import_annotations=False
        )
        self.assertFalse(
            'a' in segmentation[0].annotations,
            msg="tokenize doesn't skip importing annotations (mode tokenize)!"
        )

    def test_tokenize_create_static_annotations_tokenize(self):
        """Does tokenize create static annotations (mode tokenize)?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [(re.compile(r'\w+'), 'tokenize', {'c': '3'})],
        )
        self.assertEqual(
            [s.annotations['c'] for s in segmentation],
            ['3', '3'],
            msg="tokenize doesn't create static annotations (mode tokenize)!"
        )

    def test_tokenize_create_dynamic_annotations_tokenize(self):
        """Does tokenize create dynamic annotations (mode tokenize)?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [
                (re.compile(r'\w(\w)(\w)'), 'tokenize', {'&1': '&2'}),
            ],
        )
        self.assertEqual(
            segmentation[0].annotations['d'],
            'e',
            msg="tokenize doesn't create dynamic annotations (mode tokenize)!"
        )

    def test_tokenize_segment_split(self):
        """Does tokenize split input?"""
        segmentation = Segmenter.tokenize(
            self.entire_text_seg,
            [
                (re.compile(r'\W+'), 'split'),
                (re.compile(r'd'), 'split'),
            ],
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ab', 'ab c', 'cde', 'e'],
            msg="tokenize doesn't split input!"
        )

    def test_tokenize_import_annotations_split(self):
        """Does tokenize import annotations (mode split)?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [(re.compile(r'a'), 'split')],
        )
        self.assertEqual(
            segmentation[0].annotations['a'],
            '1',
            msg="tokenize doesn't import annotations (mode split)!"
        )

    def test_tokenize_import_annotations_false_split(self):
        """Does tokenize skip importing annotations (mode split)?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [(re.compile(r'a'), 'split')],
            import_annotations=False
        )
        self.assertFalse(
            'a' in segmentation[0].annotations,
            msg="tokenize doesn't skip importing annotations (mode split)!"
        )

    def test_tokenize_create_static_annotations_split(self):
        """Does tokenize create static annotations (mode split)?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [(re.compile(r'\W'), 'split', {'c': '3'})],
        )
        self.assertEqual(
            [s.annotations['c'] for s in segmentation],
            ['3', '3'],
            msg="tokenize doesn't create static annotations (mode split)!"
        )

    def test_tokenize_exception_mode(self):
        """Does tokenize raise exception for unknown mode?"""
        with self.assertRaises(
            ValueError,
            msg="tokenize doesn't raise exception for unknown mode!"
        ):
            Segmenter.tokenize(
                self.entire_text_seg,
                [(re.compile(r'\W+'), 'unknown_mode')],
            )

    def test_tokenize_autonumber(self):
        """Does tokenize autonumber input segments?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [
                (re.compile(r'\w+'), 'tokenize'),
                (re.compile(r'\W+'), 'split'),
            ],
            auto_number_as='num'
        )
        self.assertEqual(
            [s.annotations['num'] for s in segmentation],
            [1, 2, 3, 4],
            msg="tokenize doesn't autonumber input segments!"
        )

    def test_tokenize_sort(self):
        """Does tokenize sort output segments?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [
                (re.compile(r'\w'), 'tokenize'),
                (re.compile(r'[ae]'), 'tokenize'),
            ],
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['a', 'a', 'b', 'c', 'd', 'e', 'e'],
            msg="tokenize doesn't sort output segments!"
        )

    def test_tokenize_merge_duplicates(self):
        """Does tokenize merge duplicates?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [
                (re.compile(r'\w+'), 'tokenize'),
                (re.compile(r'\W+'), 'split'),
            ],
            merge_duplicates=True,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ab', 'cde'],
            msg="tokenize doesn't merge duplicates!"
        )

    def test_tokenize_solve_conflicts_merge_duplicates(self):
        """Does tokenize solve conflicts when merging duplicates?"""
        segmentation = Segmenter.tokenize(
            self.word_seg,
            [
                (re.compile(r'\w+'), 'tokenize', {'a': '10'}),
                (re.compile(r'\W+'), 'split', {'a': '20'}),
            ],
            merge_duplicates=True,
        )
        self.assertEqual(
            segmentation[1].annotations['a'],
            '20',
            msg="tokenize doesn't solve conflicts when merging duplicates!"
        )

    def test_tokenize_progress(self):
        """Does tokenize track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.tokenize(
            self.word_seg,
            [(re.compile(r'\w'), 'tokenize')],
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.word_seg),
            msg="tokenize doesn't track progress!"
        )

    def test_select_select(self):
        """Does select select segments?"""
        segmentation, _ = Segmenter.select(
            self.word_seg,
            re.compile(r'\w{3,}'),
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['cde'],
            msg="select doesn't select segments!"
        )

    def test_select_select_neg(self):
        """Does select output complementary segmentation?"""
        _, segmentation = Segmenter.select(
            self.word_seg,
            re.compile(r'\w{3,}'),
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ab'],
            msg="select doesn't output complementary segmentation!"
        )

    def test_select_mode(self):
        """Does select respect mode setting?"""
        segmentation, _ = Segmenter.select(
            self.word_seg,
            re.compile(r'\w{3,}'),
            mode="exclude",
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ab'],
            msg="select doesn't respect mode setting!"
        )

    def test_select_import_annotations(self):
        """Does select import annotations?"""
        segmentation, _ = Segmenter.select(
            self.word_seg,
            re.compile(r'\w+'),
            copy_annotations=True,
        )
        self.assertEqual(
            segmentation[0].annotations['a'],
            '1',
            msg="select doesn't import annotations!"
        )

    def test_select_import_annotations_false(self):
        """Does select skip importing annotations?"""
        segmentation, _ = Segmenter.select(
            self.word_seg,
            re.compile(r'\w+'),
            copy_annotations=False,
        )
        self.assertFalse(
            'a' in segmentation[0].annotations,
            msg="select doesn't skip importing annotations!"
        )

    def test_select_annotations(self):
        """Does select work with annotations?"""
        segmentation, _ = Segmenter.select(
            self.word_seg,
            re.compile(r'.'),
            annotation_key='a'
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ab'],
            msg="select doesn't work with annotations!"
        )

    def test_select_autonumber(self):
        """Does select autonumber input segments?"""
        segmentation, _ = Segmenter.select(
            self.char_seg,
            re.compile(r'.'),
            auto_number_as='num'
        )
        self.assertEqual(
            [s.annotations['num'] for s in segmentation],
            [1, 2, 3, 4, 5, 6],
            msg="select doesn't autonumber input segments!"
        )

    def test_select_progress(self):
        """Does select track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.select(
            self.char_seg,
            re.compile(r'.'),
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.char_seg),
            msg="select doesn't track progress!"
        )

    def test_threshold_select(self):
        """Does threshold select segments (min and max)?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
            min_count=2,
            max_count=2,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['b', 'b'],
            msg="threshold doesn't select segments (min and max)!"
        )

    def test_threshold_select_no_max(self):
        """Does threshold select segments (min, no max)?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
            min_count=2,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['b', 'b', 'c', 'c', 'c'],
            msg="threshold doesn't select segments (min, no max)!"
        )

    def test_threshold_select_no_min(self):
        """Does threshold select segments (no min, max)?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
            max_count=2,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['a', 'b', 'b'],
            msg="threshold doesn't select segments (no min, max)!"
        )

    def test_threshold_select_no_min_no_max(self):
        """Does threshold select segments (no min, no max)?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['a', 'b', 'b', 'c', 'c', 'c'],
            msg="threshold doesn't select segments (no min, no max)!"
        )

    def test_threshold_select_annotations(self):
        """Does threshold select segments using annotations?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
            min_count=2,
            max_count=2,
            annotation_key='a',
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['c', 'c'],
            msg="threshold doesn't select segments using annotations!"
        )

    def test_threshold_copy_annotations(self):
        """Does threshold copy annotations?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
            min_count=2,
            max_count=2,
            copy_annotations=True,
        )
        self.assertEqual(
            [s.annotations['a'] for s in segmentation],
            ['1', '1'],
            msg="threshold doesn't copy annotations!"
        )

    def test_threshold_copy_annotations_false(self):
        """Does threshold skip copying annotations?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
            min_count=2,
            max_count=2,
            copy_annotations=False,
        )
        self.assertEqual(
            [s for s in segmentation if 'a' in s.annotations],
            [],
            msg="threshold doesn't skip copying annotations!"
        )

    def test_threshold_autonumber(self):
        """Does threshold autonumber input segments?"""
        segmentation, _ = Segmenter.threshold(
            self.other_letter_seg,
            min_count=2,
            max_count=2,
            auto_number_as='num',
        )
        self.assertEqual(
            [s.annotations['num'] for s in segmentation],
            [1, 2],
            msg="threshold doesn't autonumber input segments!"
        )

    def test_threshold_progress(self):
        """Does threshold track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.threshold(
            self.other_letter_seg,
            min_count=2,
            max_count=2,
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.other_letter_seg),
            msg="threshold doesn't track progress!"
        )

    def test_sample_random_sample(self):
        """Does sample randomly sample segments?"""
        segmentation, _ = Segmenter.sample(
            self.char_seg,
            sample_size=4,
            mode='random',
        )
        self.assertEqual(
            len(segmentation),
            4,
            msg="sample doesn't randomly sample segments!"
        )

    def test_sample_systematic_sample(self):
        """Does sample systematically sample segments?"""
        segmentation, _ = Segmenter.sample(
            self.char_seg,
            sample_size=3,
            mode='systematic',
        )
        self.assertEqual(
            [s.start for s in segmentation],
            [0, 2, 4],
            msg="sample doesn't systematically sample segments!"
        )

    def test_sample_exception_mode(self):
        """Does sample raise exception for unknown mode?"""
        with self.assertRaises(
            ValueError,
            msg="sample doesn't raise exception for unknown mode!"
        ):
            Segmenter.sample(
                self.entire_text_seg,
                sample_size=3,
                mode='unknown_mode',
            )

    def test_sample_neg(self):
        """Does sample output complementary segmentation?"""
        _, segmentation = Segmenter.sample(
            self.char_seg,
            sample_size=4,
            mode='random',
        )
        self.assertEqual(
            len(segmentation),
            2,
            msg="sample doesn't output complementary segmentation!"
        )

    def test_sample_import_annotations(self):
        """Does sample import annotations?"""
        segmentation, _ = Segmenter.sample(
            self.single_letter_seg,
            sample_size=1,
            copy_annotations=True,
        )
        self.assertEqual(
            segmentation[0].annotations['b'],
            '1',
            msg="sample doesn't import annotations!"
        )

    def test_sample_import_annotations_false(self):
        """Does sample skip importing annotations?"""
        segmentation, _ = Segmenter.sample(
            self.single_letter_seg,
            sample_size=1,
            copy_annotations=False,
        )
        self.assertFalse(
            'b' in segmentation[0].annotations,
            msg="sample doesn't import annotations!"
        )

    def test_sample_autonumber(self):
        """Does sample autonumber input segments?"""
        segmentation, _ = Segmenter.sample(
            self.char_seg,
            sample_size=4,
            mode='random',
            auto_number_as='num'
        )
        self.assertEqual(
            [s.annotations['num'] for s in segmentation],
            [1, 2, 3, 4],
            msg="sample doesn't autonumber input segments!"
        )

    def test_sample_progress(self):
        """Does sample track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.sample(
            self.char_seg,
            sample_size=4,
            mode='random',
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.char_seg),
            msg="sample doesn't track progress!"
        )

    def test_intersect_content_content(self):
        """Does intersect filter segments (content content)?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
        )
        self.assertEqual(
            ''.join(s.get_content() for s in segmentation),
            'bd',
            msg="intersect doesn't filter segments (content content)!"
        )

    def test_intersect_annotation_content(self):
        """Does intersect filter segments (annotation content)?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            source_annotation_key='a',
        )
        self.assertEqual(
            ''.join(s.get_content() for s in segmentation),
            'a',
            msg="intersect doesn't filter segments (annotation content)!"
        )

    def test_intersect_content_annotation(self):
        """Does intersect filter segments (content annotation)?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            filtering_annotation_key='a',
        )
        self.assertEqual(
            ''.join(s.get_content() for s in segmentation),
            'b',
            msg="intersect doesn't filter segments (content annotation)!"
        )

    def test_intersect_annotation_annotation(self):
        """Does intersect filter segments (annotation annotation)?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            source_annotation_key='b',
            filtering_annotation_key='a',
        )
        self.assertEqual(
            ''.join(s.get_content() for s in segmentation),
            'd',
            msg="intersect doesn't filter segments (annotation annotation)!"
        )

    def test_intersect_neg(self):
        """Does intersect output complementary segmentation?"""
        _, segmentation = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
        )
        self.assertEqual(
            ''.join(s.get_content() for s in segmentation),
            'ace',
            msg="intersect doesn't output complementary segmentation!"
        )

    def test_intersect_mode(self):
        """Does intersect respect mode setting?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            mode="exclude",
        )
        self.assertEqual(
            ''.join(s.get_content() for s in segmentation),
            'ace',
            msg="intersect doesn't respect mode setting!"
        )

    def test_intersect_import_annotations(self):
        """Does intersect import annotations?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            source_annotation_key='a',
            copy_annotations=True,
        )
        self.assertEqual(
            segmentation[0].annotations['a'],
            '1',
            msg="intersect doesn't import annotations!"
        )

    def test_intersect_import_annotations_false(self):
        """Does intersect skip importing annotations?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            source_annotation_key='a',
            copy_annotations=False,
        )
        self.assertFalse(
            'a' in segmentation[0].annotations,
            msg="intersect doesn't skip importing annotations!"
        )

    def test_intersect_autonumber(self):
        """Does intersect autonumber input segments?"""
        segmentation, _ = Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            auto_number_as='num'
        )
        self.assertEqual(
            [s.annotations['num'] for s in segmentation],
            [1, 2],
            msg="intersect doesn't autonumber input segments!"
        )

    def test_intersect_progress(self):
        """Does intersect track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.intersect(
            source=self.letter_seg,
            filtering=self.third_letter_seg,
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.letter_seg),
            msg="intersect doesn't track progress!"
        )

    def test_import_xml_segment_elements(self):
        """Does import_xml segment xml elements?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['<a attr="2">c<a/>d</a>', 'c<a/>d'],
            msg="import_xml doesn't segment xml elements!"
        )

    def test_import_xml_segment_elements_broken(self):
        """Does import_xml segment xml elements from distinct strings?"""
        segmentation = Segmenter.import_xml(
            self.broken_xml_seg,
            element='a',
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['1<a>2<a>3</a>4', '2<a>3</a>4', '3', '</a>5'],
            msg="import_xml doesn't segment elements from distinct strings!"
        )

    def test_import_xml_exception_missing_closing(self):
        """Does import_xml detect missing closing tag?"""
        with self.assertRaises(
            ValueError,
            msg="import_xml doesn't detect missing closing tag!"
        ):
            Segmenter.import_xml(
                self.wrong_xml_seg,
                element='a',
            )

    def test_import_xml_exception_missing_opening(self):
        """Does import_xml detect missing opening tag?"""
        with self.assertRaises(
            ValueError,
            msg="import_xml doesn't detect missing opening tag!"
        ):
            Segmenter.import_xml(
                self.wrong_xml_seg2,
                element='a',
            )

    def test_import_xml_convert_attributes(self):
        """Does import_xml convert attributes?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
        )
        self.assertEqual(
            [s.annotations['attr'] for s in segmentation],
            ['1', '2'],
            msg="import_xml doesn't convert attributes!"
        )

    def test_import_xml_condition(self):
        """Does import_xml respect conditions?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
            conditions={'attr': re.compile(r'^2$')},
        )
        self.assertEqual(
            [s.annotations['attr'] for s in segmentation],
            ['2'],
            msg="import_xml doesn't respect conditions!"
        )

    def test_import_xml_remove_markup(self):
        """Does import_xml remove markup?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
            conditions={'attr': re.compile(r'^2$')},
            remove_markup=True,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['c', 'd'],
            msg="import_xml doesn't remove markup!"
        )

    def test_import_xml_remove_markup_broken(self):
        """Does import_xml remove markup from distinct strings?"""
        segmentation = Segmenter.import_xml(
            self.broken_xml_seg,
            element='a',
            remove_markup=True,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['1', '2', '2', '3', '3', '3', '4', '4', '5'],
            msg="import_xml doesn't remove markup from distinct strings!"
        )

    def test_import_xml_merge_duplicates(self):
        """Does import_xml merge duplicates?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
            merge_duplicates=True,
            remove_markup=True,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['c', 'd'],
            msg="import_xml doesn't merge duplicates!"
        )

    def test_import_xml_import_annotations(self):
        """Does import_xml import annotations?"""
        segmentation = Segmenter.import_xml(
            self.broken_xml_seg,
            element='a',
            import_annotations=True,
        )
        self.assertEqual(
            segmentation[0].annotations['a'],
            '1',
            msg="import_xml doesn't import annotations!"
        )

    def test_import_xml_import_annotations_false(self):
        """Does import_xml skip importing annotations?"""
        segmentation = Segmenter.import_xml(
            self.broken_xml_seg,
            element='a',
            import_annotations=False,
        )
        self.assertFalse(
            'a' in segmentation[0].annotations,
            msg="import_xml doesn't skip importing annotations!"
        )

    def test_import_xml_import_element_as_annotation(self):
        """Does import_xml import element as annotation?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
            import_element_as='test',
        )
        self.assertEqual(
            [s.annotations['test'] for s in segmentation],
            ['a', 'a'],
            msg="import_xml doesn't import element as annotation!"
        )

    def test_import_xml_solve_attribute_conflict(self):
        """Does import_xml solve attribute conflicts?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
            merge_duplicates=True,
            remove_markup=True,
        )
        self.assertEqual(
            segmentation[0].annotations['attr'],
            '1',
            msg="import_xml doesn't solve attribute conflicts!"
        )

    def test_import_xml_preserve_leaves(self):
        """Does import_xml preserve leaves?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
            merge_duplicates=True,
            remove_markup=True,
            preserve_leaves=True,
        )
        self.assertEqual(
            segmentation[0].annotations['attr'],
            '2',
            msg="import_xml doesn't preserve leaves!"
        )

    def test_import_xml_autonumber(self):
        """Does import_xml autonumber input segments?"""
        segmentation = Segmenter.import_xml(
            self.xml_seg,
            element='a',
            auto_number_as='num'
        )
        self.assertEqual(
            [s.annotations['num'] for s in segmentation],
            [1, 2],
            msg="import_xml doesn't autonumber input segments!"
        )

    def test_import_xml_progress(self):
        """Does import_xml track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.import_xml(
            self.broken_xml_seg,
            element='a',
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.broken_xml_seg),
            msg="import_xml doesn't track progress!"
        )

    def test_recode_single_input(self):
        """Does recode return a single Input object when needed?"""
        segmentation = Segmenter.recode(
            self.entire_text_seg,
            case='upper',
        )
        self.assertTrue(
            isinstance(segmentation, Input),
            msg="recode doesn't return a single Input object when needed!"
        )

    def test_recode_no_change(self):
        """Does recode return a Segmentation when no change is made?"""
        segmentation = Segmenter.recode(
            self.entire_text_seg,
        )
        self.assertTrue(
            isinstance(segmentation, Segmentation),
            msg="recode doesn't return a Segmentation when no change is made!"
        )

    def test_recode_segmentation_as_input(self):
        """Does recode return a Segmentation when input is one?"""
        segmentation = Segmenter.recode(
            self.letter_seg,
            case='upper',
        )
        self.assertTrue(
            isinstance(segmentation, Segmentation),
            msg="recode doesn't return a Segmentation when input is one!"
        )

    def test_recode_overlapping_segmentation(self):
        """Does recode raise exception for overlapping segmentation?"""
        with self.assertRaises(
            ValueError,
            msg="recode doesn't raise exception for overlapping segmentation!"
        ):
            Segmenter.recode(
                self.overlapping_seg,
            )

    def test_recode_upper_case(self):
        """Does recode change case to upper?"""
        segmentation = Segmenter.recode(
            self.word_seg,
            case='upper',
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['AB', 'CDE'],
            msg="recode doesn't change case to upper!"
        )

    def test_recode_lower_case(self):
        """Does recode change case to lower?"""
        segmentation = Segmenter.recode(
            self.second_word_seg,
            case='lower',
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ab', 'cd\xe9'],
            msg="recode doesn't change case to lower!"
        )

    def test_recode_remove_accents(self):
        """Does recode remove accents?"""
        segmentation = Segmenter.recode(
            self.second_word_seg,
            remove_accents=True,
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['AB', 'cde'],
            msg="recode doesn't remove accents!"
        )

    def test_recode_substitutions(self):
        """Does recode apply substitutions?"""
        segmentation = Segmenter.recode(
            self.word_seg,
            substitutions=[
                (re.compile(r'..'), 'x'),
                (re.compile(r'xe'), 'ex'),
            ],
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['x', 'ex'],
            msg="recode doesn't apply substitutions!"
        )

    def test_recode_substitutions_after(self):
        """Does recode apply substitutions after preprocessing?"""
        segmentation = Segmenter.recode(
            self.word_seg,
            case='upper',
            substitutions=[
                (re.compile(r'..'), 'x'),
                (re.compile(r'xe'), 'ex'),
            ],
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['x', 'xE'],
            msg="recode doesn't apply substitutions after preprocessing!"
        )

    def test_recode_variable_interpolation(self):
        """Does recode interpolate variables for substitutions?"""
        segmentation = Segmenter.recode(
            self.word_seg,
            substitutions=[
                (re.compile(r'(.)(.)'), '&2&1'),
            ],
        )
        self.assertEqual(
            [s.get_content() for s in segmentation],
            ['ba', 'dce'],
            msg="recode doesn't interpolate variables for substitutions!"
        )

    def test_recode_copy_annotations(self):
        """Does recode copy annotations?"""
        segmentation = Segmenter.recode(
            self.word_seg,
            substitutions=[
                (re.compile(r'...'), 'test'),
            ],
            copy_annotations=True,
        )
        self.assertEqual(
            segmentation[0].annotations['a'],
            '1',
            msg="recode doesn't copy annotations!"
        )

    def test_recode_copy_annotations_false(self):
        """Does recode skip copying annotations?"""
        segmentation = Segmenter.recode(
            self.word_seg,
            substitutions=[
                (re.compile(r'...'), 'test'),
            ],
            copy_annotations=False,
        )
        self.assertFalse(
            'a' in segmentation[0].annotations,
            msg="recode doesn't skip copying annotations!"
        )

    def test_recode_progress(self):
        """Does recode track progress?"""

        def progress_callback():
            """Mock progress callback"""
            self.count += 1

        Segmenter.recode(
            self.word_seg,
            case='upper',
            substitutions=[
                (re.compile(r'..'), 'x'),
                (re.compile(r'xe'), 'ex'),
            ],
            progress_callback=progress_callback,
        )
        self.assertEqual(
            self.count,
            len(self.word_seg),
            msg="recode doesn't track progress!"
        )

    def test_bypass_copy_segments(self):
        """Does bypass copy input segments?"""
        segmentation = Segmenter.bypass(self.letter_seg)
        self.assertEqual(
            [s.get_content() for s in segmentation],
            [s.get_content() for s in self.letter_seg],
            msg="bypass doesn't copy input segments!"
        )

    def test_bypass_copy_annotations(self):
        """Does bypass copy annotations?"""
        segmentation = Segmenter.bypass(self.other_letter_seg)
        self.assertEqual(
            [s.annotations['a'] for s in segmentation],
            [s.annotations['a'] for s in self.other_letter_seg],
            msg="bypass doesn't copy annotations!"
        )

    def test_bypass_deepcopy(self):
        """Does bypass deep copy input segments?"""
        segmentation = Segmenter.bypass(self.letter_seg)
        self.assertNotEqual(
            segmentation.segments,
            self.letter_seg.segments,
            msg="bypass doesn't deep copy input segments!"
        )

    def test_merge_duplicate_segments(self):
        """Does _merge_duplicate_segments merge duplicates?"""
        segments = Segmenter._merge_duplicate_segments(
            self.duplicate_seg.segments
        )
        self.assertEqual(
            [s.get_content() for s in segments],
            ['a'],
            msg="_merge_duplicate_segments doesn't merge duplicates!"
        )

    def test_auto_number_autonumber(self):
        """Does _auto_number autonumber in place?"""
        Segmenter._auto_number(
            self.third_letter_seg.segments,
            annotation_key='num',
        )
        self.assertEqual(
            [s.annotations['num'] for s in self.third_letter_seg.segments],
            [1, 2, 3],
            msg="_auto_number doesn't autonumber in place!"
        )

    def test_parse_xml_tag_is_element(self):
        """Does _parse_xml_tag recognize xml elements?"""
        tags = [
            Segmenter._parse_xml_tag('<a>'),
            Segmenter._parse_xml_tag('<a attr="1">'),
            Segmenter._parse_xml_tag('</a>'),
            Segmenter._parse_xml_tag('<a/>'),
            Segmenter._parse_xml_tag('<!-- test -->'),
            Segmenter._parse_xml_tag('<!test>'),
            Segmenter._parse_xml_tag('<?test?>'),
        ]
        self.assertEqual(
            [tag['is_element'] for tag in tags],
            [True for _ in range(4)] + [False for _ in range(3)],
            msg="_parse_xml_tag doesn't recognize xml elements!"
        )

    def test_parse_xml_tag_element_name(self):
        """Does _parse_xml_tag parse element name?"""
        tags = [
            Segmenter._parse_xml_tag('<a>'),
            Segmenter._parse_xml_tag('<a attr="1">'),
            Segmenter._parse_xml_tag('</a>'),
            Segmenter._parse_xml_tag('<a/>'),
        ]
        self.assertEqual(
            [tag['element'] for tag in tags],
            ['a', 'a', 'a', 'a'],
            msg="_parse_xml_tag doesn't parse element name!"
        )

    def test_parse_xml_tag_is_opening(self):
        """Does _parse_xml_tag recognize opening tags?"""
        tags = [
            Segmenter._parse_xml_tag('<a>'),
            Segmenter._parse_xml_tag('<a attr="1"/>'),
            Segmenter._parse_xml_tag('</a>'),
        ]
        self.assertEqual(
            [tag['is_opening'] for tag in tags],
            [True, True, False],
            msg="_parse_xml_tag doesn't recognize opening tags!"
        )

    def test_parse_xml_tag_is_empty(self):
        """Does _parse_xml_tag recognize empty elements?"""
        tags = [
            Segmenter._parse_xml_tag('<a>'),
            Segmenter._parse_xml_tag('</a>'),
            Segmenter._parse_xml_tag('<a/>'),
            Segmenter._parse_xml_tag('<a attr="1"/>'),
        ]
        self.assertEqual(
            [tag['is_empty'] for tag in tags],
            [False, False, True, True],
            msg="_parse_xml_tag doesn't recognize empty elements!"
        )

    def test_parse_xml_tag_attributes(self):
        """Does _parse_xml_tag parse attributes?"""
        tag = Segmenter._parse_xml_tag('<a attr1="2" attr3="4">')
        self.assertEqual(
            tag['attributes'],
            {'attr1': '2', 'attr3': '4'},
            msg="_parse_xml_tag doesn't parse attributes!"
        )


if __name__ == '__main__':
    unittest.main()
