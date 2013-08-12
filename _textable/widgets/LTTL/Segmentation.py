#=============================================================================
# Class LTTL.Segmentation, v0.20
# Copyright 2012-2013 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the LTTL package v1.3
#
# LTTL v1.3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LTTL v1.3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LTTL v1.3. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

import codecs, re

class Segmentation(object):

    """A class for representing a segmentation."""
    
    # Class variable to store the data.
    data = []

    def __init__(self, segments=None, label=u'my_segmentation'):
        """Initialize a Segmentation instance"""
        if segments is None:
            segments = []
        self.segments = segments
        self.label    = label

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
        del self.values[index]

    def __iter__(self):
        """Return an iterator on segments"""
        return iter(self.segments)
        
    def to_string(
            self,
            format              = None,
            segment_delimiter   = u'\n',
            humanize_addresses  = False,
            progress_callback   = None,
        ):
        """Stringify a segmentation"""
        if humanize_addresses:
            offset = 1
        else:
            offset = 0
        if format:
            default_dict = dict(
                    (k, u'__none__') for k in self.get_annotation_keys()
            )
            for match in re.finditer(r'(?<=%\()(.+?)(?=\))', format):
                default_dict[match.group(0)] = u'__none__'
        segment_count = 1
        lines = []
        for segment in self.segments:
            address   = segment.address
            str_index = address.str_index + offset
            start     = (address.start or 0) + offset
            end = address.end or len(Segmentation.data[address.str_index])
            if format:
                segment_dict = default_dict.copy()
                segment_dict.update(segment.annotations)
                segment_dict['__num__']       = segment_count
                segment_dict['__content__']   = segment.get_content()
                segment_dict['__str_index__'] = str_index
                segment_dict['__start__']     = start
                segment_dict['__end__']       = end
                lines.append(format % segment_dict)
            else:
                lines.extend([
                        u'segment number %i'% segment_count,
                        u'\tcontent:\t"%s"' % segment.get_content(),
                        u'\tstr_index:\t%i' % str_index,
                        u'\tstart:\t%i'     % start,
                        u'\tend:\t%i'       % end
                ])
                if len(segment.annotations):
                    lines.append(u'\tannotations:')
                    lines.extend([
                            u'\t\t%-20s %s' % (k, v)
                                for (k, v) in segment.annotations.items()
                    ])
            segment_count += 1
            if progress_callback:
                progress_callback()
        return segment_delimiter.join(lines)

    def to_html(self, humanize_addresses=False, progress_callback=None):
        """Stringify a segmentation in html format"""
        if humanize_addresses:
            offset = 1
        else:
            offset = 0
        html_header = u"""
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
        html_footer           = u'</body></html>'
        table_header          = u'<p><table class="textable">'
        wide_table_header     = u'<p><table class="textable" width="100%">'
        table_footer          = u'</table></p>'
        first_row_address     = u'<tr><th align="left">String index</th>'   \
                              + u'<th align="left">Start</th>'              \
                              + u'<th align="left">End</th></tr>'
        first_row_annotation  = u'<tr><th align="left">Annotation key</th>' \
                              + u'<th align="left">Annotation value</th></tr>'
        first_row_content     = u'<tr><th align="left">Content</th></tr>'
        data    = Segmentation.data
        counter = 1
        lines   = [u'<h2>%s</h2>' % self.label]
        for segment in self.segments:
            address =  segment.address
            start   =  address.start or 0
            end     =  address.end or len(data[address.str_index])
            address_string = u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (
                    address.str_index + offset,
                    start + offset,
                    end,
            )
            annotation_string = ''.join([
                    u'<tr><td>%s</td><td>%s</td></tr>' % (k, v)
                            for (k, v) in segment.annotations.items()
            ])
            content = segment.get_content().replace('<', '&lt;')
            content = content.replace('>', '&gt;')
            content = content.replace('\n', '<br/>')
            lines.extend([
                    #u'<h3>Segment #%i</h3>' % counter,
                    u'<h3>Segment #%i</h3><a name="%i"/>' % (counter, counter),
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
                    u'<tr><td>%s</td></tr>' % content,
                    table_footer,
            ])
            counter += 1
            if progress_callback:
                progress_callback()
        return html_header + '\n'.join(lines) + html_footer

    def append(self, segment):
        """Add a segment at the end of the segmentation"""
        self.segments.append(segment)

    def get_annotation_keys(self):
        """Get the list of available annotation keys"""
        annotation_keys = set()
        for segment in self.segments:
            annotation_keys = annotation_keys.union(
                segment.annotations.keys()
            )
        return list(annotation_keys)
        
    def is_non_overlapping(self):
        """Determine if there is no segment overlap"""
        segments = sorted(self.segments, key=lambda s: (
                s.address.str_index,
                s.address.start,
                s.address.end,
        ))
        for first_index in xrange(len(segments)-1):
            first_address   = self.segments[first_index].address
            first_str_index = first_address.str_index
            first_start     = first_address.start or 0
            text_length     = len(Segmentation.data[first_str_index])
            first_end       = first_address.end or text_length
            for second_index in xrange(first_index+1, len(segments)):
                second_address      = self.segments[second_index].address
                second_str_index    = second_address.str_index
                if second_str_index != first_str_index:
                    break
                second_start = second_address.start or 0
                if second_start >= first_end:
                    break
                second_end = second_address.end or text_length
                if second_end > second_start:
                    return False
        return True








