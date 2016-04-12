"""
Module Segmentation.py, v0.23
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

import re

from past.builtins import xrange
from builtins import dict


class Segmentation(object):
    """A class for representing a segmentation."""

    # Class variable to store the data.
    data = list()

    def __init__(self, segments=None, label='segmented_data'):
        """Initialize a Segmentation instance"""
        if segments is None:
            segments = list()
        self.segments = segments
        self.label = label

    def __len__(self):
        """Return the number of segments in the segmentation"""
        return len(self.segments)

    def __getitem__(self, index):
        """Return the value of a given segment"""
        return self.segments[index]

    def __setitem__(self, index, value):
        """Set the value of a given segment"""
        self.segments[index] = value

    def __delitem__(self, index):
        """Delete a given segment"""
        del self.segments[index]

    def __iter__(self):
        """Return an iterator on segments"""
        return iter(self.segments)

    # TODO: update client code to match signature change (format=>formatting)
    def to_string(
            self,
            formatting=None,
            segment_delimiter='\n',
            header='',
            footer='',
            humanize_addresses=False,
            progress_callback=None,
    ):
        """Stringify a segmentation

        :param formatting: format string for each segment (default None)

        :param segment_delimiter: string inserted between consecutive segments
        (default '\n')

        :param header: string inserted at beginning of output string (default
        '')

        :param footer: string inserted at end of output string (default '')

        :param humanize_addresses: boolean indicating whether string indices as
        well as start positions in strings should be numbered from 1, rather
        than from 0 as usual (default False)

        :param progress_callback: callback for monitoring progress ticks (number
        of input segments)

        :return: formatted string

        In format string, it is possible to use the %(variable_name) format
        notation to insert variable element in each segment's formatted string,
        cf. https://orange-textable.readthedocs.org/en/latest/display.html.
        """

        # Add (or not) a 1-unit offset to make addresses more readable.
        offset = 1 if humanize_addresses else 0

        # If a format has been specified, initialize default annotation dict
        # based on existing annotations or those referred to in format...
        if formatting is not None:
            default_dict = dict(
                (k, '__none__') for k in self.get_annotation_keys()
            )
            for match in re.finditer(r'(?<=%\()(.+?)(?=\))', formatting):
                default_dict[match.group(0)] = '__none__'

        # Initializations...
        segment_count = 1
        lines = list()

        # Process each segment...
        for segment in self.segments:
            str_index = segment.str_index + offset
            start = (segment.start or 0) + offset
            end = segment.end or len(Segmentation.data[segment.str_index])

            # If a format has been specified...
            if formatting is not None:

                # Clone default annotations and update them with existing...
                segment_dict = default_dict.copy()
                segment_dict.update(segment.annotations)

                # Update annotations with predefined variables...
                segment_dict['__num__'] = segment_count
                segment_dict['__content__'] = segment.get_content()
                segment_dict['__str_index__'] = str_index
                segment_dict['__start__'] = start
                segment_dict['__end__'] = end
                segment_dict['__str_index_raw__'] = str_index - offset
                segment_dict['__start_raw__'] = start - offset
                segment_dict['__end_raw__'] = end

                # Apply format and add resulting line to list for later output.
                lines.append(formatting % segment_dict)

            # Else if no format has been specified...
            else:

                # Add lines in predefined format to list for later output...
                lines.extend([
                    'segment number %i' % segment_count,
                    '\tcontent:\t"%s"' % segment.get_content(),
                    '\tstr_index:\t%i' % str_index,
                    '\tstart:\t%i' % start,
                    '\tend:\t%i' % end,
                ])

                # Add annotations (if any) in predefined format...
                if len(segment.annotations):
                    lines.append('\tannotations:')
                    lines.extend(
                        [
                            '\t\t%-20s %s' % (k, v)
                            for (k, v) in sorted(segment.annotations.items())
                        ]
                    )

            segment_count += 1
            if progress_callback:
                progress_callback()

        # Join lines and append header and footer (if any).
        if formatting:
            return header + segment_delimiter.join(lines) + footer
        else:
            return header + '\n'.join(lines) + footer

    # TODO: test
    def to_html(self, humanize_addresses=False, progress_callback=None):
        """Stringify a segmentation in HTML format

        :param humanize_addresses: boolean indicating whether positions in
        strings should be numbered from 1, rather than from 0 as usual (default
        False)

        :param progress_callback: callback for monitoring progress ticks (number
        of input segments)

        :return: HTML formatted string
        """

        # Add (or not) a 1-unit offset to make addresses more readable.
        offset = 1 if humanize_addresses else 0

        # Define HTML header, footer and other template elements...
        html_header = """
            <html><head><style type="text/css">
                table.textable {
                    border-width: 1px;
                    border-style: solid;
                    border-color: gray;
                    background-color: white;
                }
                table.textable th {
                    border-width: 0px;
                    padding: 3px;
                    background-color: lightgray;
                }
                table.textable td {
                    border-width: 0px;
                    padding: 3px;
                }
            </style></head><body><a name="top"/>
        """
        html_footer = '</body></html>'
        table_header = '<p><table class="textable">'
        wide_table_header = '<p><table class="textable" width="100%">'
        table_footer = '</table></p>'
        first_row_address = '<tr><th align="left">String index</th>' \
                            + '<th align="left">Start</th>' \
                            + '<th align="left">End</th></tr>'
        first_row_annotation = '<tr><th align="left">Annotation key</th>' \
                               + '<th align="left">Annotation value</th></tr>'
        first_row_content = '<tr><th align="left">Content</th></tr>'

        # Initializations...
        data = Segmentation.data
        counter = 1
        lines = ['<h2>%s</h2>' % self.label]

        # For each segment...
        for segment in self.segments:

            # Format address section...
            str_index = segment.str_index
            start = segment.start or 0
            end = segment.end or len(data[str_index])
            address_string = '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                str_index + offset,
                start + offset,
                end,
            )

            # Format annotation section...
            annotation_string = ''.join(
                '<tr><td>%s</td><td>%s</td></tr>' % (k, v)
                for (k, v) in sorted(segment.annotations.items())
            )

            # Replace tag delimiters with HTML entities and CR with HTML tag...
            content = segment.get_content().replace('<', '&lt;')
            content = content.replace('>', '&gt;')
            content = content.replace('\n', '<br/>')

            # Add formatted HTML for this segment...
            lines.extend([
                # '<h3>Segment #%i</h3>' % counter,
                '<h3>Segment #%i</h3><a name="%i"/>' % (counter, counter),
                table_header,
                first_row_address,
                address_string,
                table_footer,
            ])
            if len(segment.annotations):
                lines.extend([
                    table_header,
                    first_row_annotation,
                    annotation_string,
                    table_footer,
                ])
            lines.extend([
                wide_table_header,
                first_row_content,
                '<tr><td>%s</td></tr>' % content,
                table_footer,
            ])

            counter += 1
            if progress_callback:
                progress_callback()

        # Join lines and append HTML header and footer.
        return html_header + '\n'.join(lines) + html_footer

    def append(self, segment):
        """Add a segment at the end of the segmentation

        :param segment: the segment to add
        """
        self.segments.append(segment)

    def get_annotation_keys(self):
        """Get the list of available annotation keys"""

        # Initialize empty set.
        annotation_keys = set()

        # Take the union of each segment's annotation keys...
        for segment in self.segments:
            annotation_keys = annotation_keys.union(
                list(segment.annotations)
            )

        return list(annotation_keys)

    def is_non_overlapping(self):
        """Determine if there is no segment overlap"""

        # Get list of segments sorted by address...
        segments = sorted(self.segments, key=lambda s: (
            s.str_index,
            s.start,
            s.end,
        ))

        # For each segment (but the last)...
        for first_index in xrange(len(segments) - 1):

            # Get the segment's address...
            first_segment = self.segments[first_index]
            first_str_index = first_segment.str_index
            first_string_length = len(Segmentation.data[first_str_index])
            first_end = first_segment.end or first_string_length

            # For each segment after this one...
            for second_index in xrange(first_index + 1, len(segments)):
                second_segment = self.segments[second_index]
                if second_segment.str_index != first_str_index:
                    continue
                if (second_segment.start or 0) < first_end:
                    return False

        return True
