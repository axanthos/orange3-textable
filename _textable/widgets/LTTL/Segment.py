"""
Module Segment.py, v0.25
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

from operator import itemgetter
from itertools import groupby

import numpy as np
import operator

from .Segmentation import Segmentation

from builtins import range


class Segment(object):
    """A class for representing a Segmentation, with Numpy constructor"""

    __slots__ = ['str_index', 'start', 'end', 'annotations']

    def __init__(self, str_index, start=None, end=None, annotations=None):
        """Initialize a Segment instance"""
        if isinstance(str_index, (np.ndarray, list)):
            self.str_index = str_index[0]
            self.start = str_index[1]
            self.end = str_index[2]
            if start is None:
                self.annotations = {}
            else:
                self.annotations = start
        else:
            self.str_index = str_index
            if start is None:
                self.start = 0
            else:
                self.start = start
            if end is None:
                self.end = np.iinfo(np.int32).max
            else:
                self.end = end
            if annotations is None:
                self.annotations = {}
            else:
                self.annotations = annotations

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.str_index == other.str_index and \
                   self.start == (other.start or 0) and \
                   self.end == (other.end or np.iinfo(np.int32).max)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(
            [
                getter(self)
                for getter in [
                    operator.attrgetter(attr) for attr in self.__slots__
                ]
            ]
        )

    def to_string(
        self,
        formatting=None,
        segment_delimiter='\n',
        humanize_addresses=False,
        segment_count=0,
        default_dict=None,
        progress_callback=None,
    ):
        """Stringify a segmentation

        :param formatting: format string for each segment (default None)

        :param segment_delimiter: string inserted between consecutive segments
        (default '\n')

        :param humanize_addresses: boolean indicating whether string indices as
        well as start positions in strings should be numbered from 1, rather
        than from 0 as usual (default False)

        :return: formatted string

        In format string, it is possible to use the %(variable_name) format
        notation to insert variable element in each segment's formatted string,
        cf. https://orange-textable.readthedocs.org/en/latest/display.html.
        """

        # Add (or not) a 1-unit offset to make addresses more readable.
        offset = 1 if humanize_addresses else 0

        str_index = self.str_index + offset
        start = (self.start or 0) + offset
        end = self.end or len(Segmentation.data[self.str_index])

        if progress_callback:
            progress_callback()

        # If a format has been specified...
        if formatting is not None:
            # Clone default annotations and update them with existing...
            segment_dict = default_dict.copy()
            segment_dict.update(self.annotations)

            # Update annotations with predefined variables...
            segment_dict['__num__'] = segment_count
            segment_dict['__content__'] = self.get_content()
            segment_dict['__str_index__'] = str_index
            segment_dict['__start__'] = start
            segment_dict['__end__'] = end
            segment_dict['__str_index_raw__'] = str_index - offset
            segment_dict['__start_raw__'] = start - offset
            segment_dict['__end_raw__'] = end

            # Apply format and add resulting line to list for later output.
            return formatting % segment_dict

            # Else if no format has been specified...
        else:
            # Add lines in predefined format to list for later output...

            a = 'segment number %i%s\tcontent:\t"%s"%s\tstr_index:\t%i%s\tstart:\t%i%s\tend:\t%i' %     \
                (
                    segment_count,
                    segment_delimiter,
                    self.get_content(),
                    segment_delimiter,
                    str_index,
                    segment_delimiter,
                    start,
                    segment_delimiter,
                    end,
                )

            # Add annotations (if any) in predefined format...
            if len(self.annotations):
                a += '\n\tannotations:%s' % segment_delimiter
                a += '\n'.join(
                    [
                        '\t\t%-20s %s' % (k, v)
                        for (k, v) in sorted(self.annotations.items())
                    ]
                )
            return a

    def to_html(
            self,
            offset=0,
            counter=0,
            table_header='',
            first_row_address='',
            first_row_annotation='',
            first_row_content='',
            wide_table_header='',
            table_footer='',
            progress_callback=None
    ):
        """Stringify a segmentation in HTML format and returns an iterator.
        Useful when the actual string doesn't fit in memory.

        :param humanize_addresses: boolean indicating whether positions in
        strings should be numbered from 1, rather than from 0 as usual (default
        False)

        :param progress_callback: callback for monitoring progress ticks (number
        of input segments)

        :return: HTML formatted string
        """

        # Add (or not) a 1-unit offset to make addresses more readable.

        string = ''

        if progress_callback:
            progress_callback()

        # Format address section...
        str_index = self.str_index
        start = self.start or 0
        end = self.end or len(Segmentation.data[str_index])
        address_string = '<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n' % (
            str_index + offset,
            start + offset,
            end,
        )

        # Format annotation section...
        annotation_string = ''.join(
            '<tr><td>%s</td><td>%s</td></tr>\n' % (k, v)
            for (k, v) in sorted(self.annotations.items())
        )

        # Replace tag delimiters with HTML entities and CR with HTML tag...
        content = self.get_content().replace('<', '&lt;')
        content = content.replace('>', '&gt;')
        content = content.replace('\n', '<br/>')

        # Add formatted HTML for this segment...
        # yield '<h3>Segment #%i</h3>\n' % counter
        string += '<h3>Segment #%i</h3><a name="%i"/>\n' % (counter, counter)

        string += table_header

        string += first_row_address
        string += address_string
        string += table_footer

        if len(self.annotations):
            string += table_header
            string += first_row_annotation
            string += annotation_string
            string += table_footer

        string += wide_table_header
        string += first_row_content
        string += '<tr><td>%s</td></tr>\n' % content
        string += table_footer

        return string

    def get_content(self):
        """Stringify the content of a Segment

        :return: a string with the segment's content.
        """
        return Segmentation.data[self.str_index][self.start:self.end]

    def deepcopy(self, annotations=None, update=True):
        """Return a deep copy of the segment

        :param annotations: unless set to None (default), a dictionary of
        annotation key-value pairs to be assigned to the new copy of the segment

        :param update: a boolean indicating whether the annotations specified
        in parameter 'annotations' should be added to existing annotations
        (True, default) or replace them (False); if 'annotations' is set to None
        and 'update' is False, the new segment copy will have no annotations.

        :return: a deep copy of the segment
        """
        if update:
            if self.annotations is not None:
                new_annotations = self.annotations.copy()
            else:
                new_annotations = None
            if annotations is not None:
                new_annotations.update(annotations)
        elif annotations is None:
            new_annotations = dict()
        else:
            new_annotations = annotations.copy()
        return Segment(self.str_index, self.start, self.end, new_annotations)

    def contains(self, other_segment):
        """Test if another segment (or segment sequence) is contained in
        this one

        :param other_segment: the segment whose inclusion in this one is being
        tested.

        :return: boolean
        """
        if self.str_index != other_segment.str_index:
            return False
        if (self.start or 0) > (other_segment.start or 0):
            return False
        string_length = len(Segmentation.data[self.str_index])
        if (self.end or string_length) < (other_segment.end or string_length):
            return False
        return True

    def get_contained_segments(self, segmentation):
        """Return segments from another segmentation that are contained in
        this segment

        :param segmentation: the segmentation whose segments will be returned if
        they are contained in the segments of this one.

        :return: a list of segments
        """
        str_index = self.str_index
        start = self.start or 0
        string_length = len(Segmentation.data[str_index])
        end = self.end or string_length
        return [segment for segment in segmentation if (
                str_index == segment.str_index and
                start <= (segment.start or 0) and
                end >= (segment.end or string_length))]

    def get_contained_segment_indices(self, segmentation):
        """Return indices of segments from another segmentation that are
        contained in this segment

        :param segmentation: the segmentation whose segment indices will be
        returned if they are contained in the segments of this one.

        :return: a list of segment indices
        """
        str_index = self.str_index
        start = self.start or 0
        string_length = len(Segmentation.data[str_index])
        end = self.end or string_length
        return [
            i for i in range(len(segmentation)) if (
                str_index == segmentation[i].str_index and
                start <= (segmentation[i].start or 0) and
                end >= (segmentation[i].end or string_length)
            )
        ]

    def get_contained_sequence_indices(self, segmentation, length):
        """Return indices of first position of sequences of segments from
        another segmentation that are contained in this segment

        :param segmentation: the segmentation whose segment indices will be
        returned if they are contained in the segments of this one.

        :param length: the length of segment sequences.

        :return: a list of segment indices
        """
        contained_indices = self.get_contained_segment_indices(segmentation)
        # Find runs of consecutive contained indices
        # (cf. https://docs.python.org/2.6/library/itertools.html#examples)
        contained_idx_sequences = [
            list(map(itemgetter(1), g)) for _, g in groupby(
                enumerate(contained_indices),
                lambda args: args[0] - args[1]
            )
        ]
        fixed_length_idx_sequences = list()
        for contained_idx_sequence in contained_idx_sequences:
            fixed_length_idx_sequences.extend(
                [
                    contained_idx_sequence[idx] for idx in range(
                        len(contained_idx_sequence) - length + 1
                    )
                ]
            )
        return fixed_length_idx_sequences

# Not currently used in LTTL or Textable, nor tested.
#    def contains_sequence(self, sequence):
#        """Test if a sequence of segments is contained in this one"""
#        for other_segment in sequence:
#            if not self.contains(other_segment):
#                return False
#        return True


# Not currently used in LTTL or Textable, nor tested.
#    def equals(self, other_segment):
#        """Test if another segment has the same address as this one"""
#        return self.contains(other_segment) and other_segment.contains(self)


# Not currently used in LTTL or Textable, nor tested.
#    def get_contained_sequences(self, segmentation, length):
#        """Return sequences of segments from another segmentation that are
#        contained in this segment
#        """
#        contained_sequence_indices = self.get_contained_sequence_indices(
#            segmentation, length
#        )
#        fixed_length_sequences = [
#            segmentation[idx:idx+length] for idx in contained_sequence_indices
#        ]
#        return fixed_length_sequences
