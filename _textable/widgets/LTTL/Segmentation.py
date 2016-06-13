"""
Module Segmentation.py, v0.24
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

import numpy as np
from future.utils import iteritems
import re
import os
from random import randint
from tempfile import NamedTemporaryFile
from collections import deque

# segmentation with more segments will have
# their string representation summarized
MAX_SEGMENT_STRING = 1000

# Number of top and bottom segments displayed in summary
NUM_SEGMENTS_SUMMARY = 5

# maximum number of segments per chunk
CHUNK_SIZE = 100000

# maximum number of chunks that are kept in RAM
CACHE_SIZE = 200

# contains the chunk or a reference to the file on disk
segments_cache = dict()

# list of chunk ids ordered by Least Recently Used
segments_access_time = deque()


def load_chunk(segmentation, id):
    """read a chunk file into memory and remove it"""
    file = segments_cache[(segmentation, id)]
    file = open(file.name, 'r+b')
    segments_cache[(segmentation, id)] = np.load(file)
    file.close()
    os.remove(file.name)


def unload_chunk(segmentation, id):
    """write a chunk to disk and keep its reference"""
    file = NamedTemporaryFile(delete=False)
    np.save(file, segments_cache[(segmentation, id)])
    segments_cache[(segmentation, id)] = file
    file.close()


def get_chunk(segmentation, id):
    """retreive the given chunk, either from memory or from disk.
    If it needs to be loaded from disk, check the current cache size
    and if necessary offload some chunks."""
    if not (segmentation, id) in segments_cache:
        return None
    if isinstance(segments_cache[(segmentation, id)], np.ndarray):
        segments_access_time.remove((segmentation, id))
        segments_access_time.appendleft((segmentation, id))
    else:
        while len(segments_access_time) >= CACHE_SIZE:
            k = segments_access_time.pop()
            unload_chunk(k[0], k[1])
        segments_access_time.appendleft((segmentation, id))
        load_chunk(segmentation, id)
    return segments_cache[(segmentation, id)]


def set_chunk(segmentation, id, array):
    """Replace a chunks' content"""
    get_chunk(segmentation, id)
    segments_cache[(segmentation, id)] = array
    segments_access_time.remove((segmentation, id))
    segments_access_time.appendleft((segmentation, id))


def add_chunk(segmentation, id, array):
    """Add a new chunk to the cache, also offloading if necessary"""
    if (segmentation, id) in segments_cache:
        set_chunk(segmentation, id, array)
        return True
    while len(segments_access_time) >= CACHE_SIZE:
        k = segments_access_time.pop()
        unload_chunk(k[0], k[1])
    segments_access_time.appendleft((segmentation, id))
    segments_cache[(segmentation, id)] = array
    return False


def remove_chunk(segmentation, id):
    """Delete a chunk from the cache and if necessary the corresponding file."""
    if not (segmentation, id) in segments_cache:
        return
    if isinstance(segments_cache[(segmentation, id)], np.ndarray):
        del segments_cache[(segmentation, id)]
        segments_access_time.remove((segmentation, id))
    else:
        file = segments_cache[(segmentation, id)]
        os.remove(file.name)
        del segments_cache[(segmentation, id)]


def clone_chunks(source, dst):
    """Copy all chunks related to a given "source" segmentation
    and associate them with a given "dst" segmentation."""
    for k, v in iteritems(segments_cache):
        if k[0] == source:
            s = get_chunk(k[0], k[1])
            add_chunk(dst, k[1], s.copy())


class Segmentation(object):
    data = list()

    def __init__(self, segmentation=None, label='segmented_data'):
        """Initialize a Segmentation instance"""
        # from nothing
        if segmentation is None:
            self.segments_nbr = 0
            self.segments_nbr_in_chunk = 0
            self.id_to_key = None
            self.key_to_id = None
            self.buffer = []
            self.str_index_ptr = {}
            self.label = label
        # from a list of segments
        elif isinstance(segmentation, list):
            self.segments_nbr = len(segmentation)
            self.segments_nbr_in_chunk = 0
            self.id_to_key = None
            self.key_to_id = None
            self.str_index_ptr = self._get_str_index_ptr(segmentation)
            self.buffer = segmentation
            self.label = label
        # from another segmentation
        else:
            clone_chunks(segmentation, self)
            self.id_to_key = segmentation.id_to_key
            self.key_to_id = segmentation.key_to_id
            self.buffer = segmentation.buffer
            self.segments_nbr_in_chunk = segmentation.segments_nbr_in_chunk
            self.segments_nbr = segmentation.segments_nbr
            self.str_index_ptr = segmentation.str_index_ptr
            if self.label == 'segmented_data':
                self.label = segmentation.label
            else:
                self.label = label

    def __len__(self):
        """Return the number of segments in the segmentation"""
        return self.segments_nbr

    def __getitem__(self, key):
        """Return the value of a given segment"""
        from .Segment import Segment
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            return [self[ii] for ii in range(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0:
                key = self.segments_nbr + key

            if key >= self.segments_nbr_in_chunk:
                return self.buffer[key - self.segments_nbr_in_chunk].deepcopy()
            else:
                a = get_chunk(self, key // CHUNK_SIZE + 1)
                return Segment(a[key % CHUNK_SIZE], self.get_annotation(key))

    def __setitem__(self, index, segment):
        """Set the value of a given segment"""
        if index < 0:
            index = self.segments_nbr + index
        if index >= self.segments_nbr_in_chunk:
            self.buffer[index - self.segments_nbr_in_chunk] = segment
        else:
            a = get_chunk(self, index // CHUNK_SIZE+1)
            a[index % CHUNK_SIZE] = np.array(
                [segment.str_index, segment.start, segment.end],
                dtype=np.int32
            )
            set_chunk(self, index // CHUNK_SIZE+1, a)
            if (
                segment.annotations is not None or
                len(segment.annotations) is not 0
            ):
                self.create_anotation()
                b = get_chunk(self, -(index // CHUNK_SIZE+1))
                b[index % CHUNK_SIZE] = np.array(
                    self.get_annotation_tab(segment),
                    dtype=np.int16
                )
                set_chunk(self, index // CHUNK_SIZE + 1, b)

    def __delitem__(self, index):
        """Delete a given segment"""
        raise NotImplementedError("segmentations are not directly editable")

    def __iter__(self):
        """Return an iterator on segments"""
        from .Segment import Segment
        if self.segments_nbr_in_chunk > 0:
            for i in range(1, self.segments_nbr_in_chunk // CHUNK_SIZE+1):
                a = get_chunk(self, i)
                b = get_chunk(self, -i)
                if a is not None:
                    for index in range(len(a)):
                        annotation = None
                        if b is not None:
                            annotation = dict(
                                [
                                    self.id_to_key[x]
                                    for x in b[index % CHUNK_SIZE]
                                ]
                            )
                        yield Segment(a[index % CHUNK_SIZE], annotation)
        for segment in self.buffer:
            yield segment.deepcopy()

    def _get_str_index_ptr(self, segments, before_first_segment=None, offset=0):
        """Finds at which index segments start referring to new str_index"""
        temp_ptr = {}
        last_seen = before_first_segment
        for i, s in enumerate(segments):
            if not last_seen or s.str_index != last_seen.str_index:
                temp_ptr[s.str_index] = i + offset
            last_seen = s
        return temp_ptr

    def has_annotation(self):
        return get_chunk(self, -1) is not None

    def create_anotation(self):
        if not self.has_annotation():
            nbSegment = self.segments_nbr_in_chunk
            id = -1
            while nbSegment > CHUNK_SIZE:
                add_chunk(
                    self, id, np.array(
                        [np.empty(0, dtype=np.int16) for x in range(CHUNK_SIZE)]
                    )
                )
                nbSegment -= CHUNK_SIZE
                id -= 1
            add_chunk(
                self, id, np.array(
                    [np.empty(0, dtype=np.int16) for x in range(nbSegment)]
                )
            )
            self.id_to_key = list()
            self.key_to_id = dict()

    def get_annotation_tab(self, segment):
        annotations_id = []
        for key, value in iteritems(segment.annotations):
            self.add_annotation_tuple((key, value))
            annotations_id.append(
                [
                    id for id in self.key_to_id[hash((key, value))]
                    if self.id_to_key[id] == (key, value)
                ][0]
            )
        return annotations_id

    def add_annotation_tuple(self, tuple):
        id_list = self.key_to_id.get(hash(tuple), [])
        if tuple not in [self.id_to_key[x] for x in id_list]:
            self.id_to_key.append(tuple)
            self.key_to_id[hash(tuple)] = self.key_to_id.get(hash(tuple), [])  \
                                        + [len(self.id_to_key) - 1]

    def get_annotation(self, index):
        if index >= self.segments_nbr_in_chunk:
            return self.buffer[index - self.segments_nbr_in_chunk].annotations
        else:
            a = get_chunk(self, -(index // CHUNK_SIZE + 1))
            if a is None:
                return None
            return dict([self.id_to_key[x] for x in a[index % CHUNK_SIZE]])

    def extend(self, segments):
        if self.segments_nbr > 0:
            new_ptrs = self._get_str_index_ptr(
                segments,
                self[-1],
                self.segments_nbr
            )
            new_ptrs.update(self.str_index_ptr)
        else:
            new_ptrs = self._get_str_index_ptr(segments)
        self.str_index_ptr = new_ptrs
        self.buffer += segments
        self.segments_nbr += len(segments)
        while len(self.buffer) >= CHUNK_SIZE:
            self.store()

    def append(self, segment):
        if self.segments_nbr == 0 or self[-1].str_index != segment.str_index:
            self.str_index_ptr[segment.str_index] = self.segments_nbr
        self.buffer.append(segment)
        self.segments_nbr += 1
        if len(self.buffer) >= CHUNK_SIZE:
            self.store()

    def store(self):
        from .Segment import Segment
        if self.segments_nbr_in_chunk % CHUNK_SIZE != 0:
            a = get_chunk(self, self.segments_nbr_in_chunk // CHUNK_SIZE + 1)
            b = get_chunk(self, -(self.segments_nbr_in_chunk // CHUNK_SIZE + 1))
            segments = list()
            if a is not None:
                for index in range(len(a)):
                    annotation = None
                    if b is not None:
                        annotation = dict(
                            [self.id_to_key[x] for x in b[index % CHUNK_SIZE]]
                        )
                    segments += Segment(a[index % CHUNK_SIZE], annotation)
            self.buffer = segments + self.buffer
            self.segments_nbr_in_chunk -= len(segments)
        nbelement_to_store = min(len(self.buffer), CHUNK_SIZE)
        ex_mat = np.empty([nbelement_to_store, 3], dtype=np.int32)
        ex_annotation = np.empty([nbelement_to_store], dtype=np.object)
        for index in range(nbelement_to_store):
            ex_mat[index][0] = self.buffer[index].str_index
            ex_mat[index][1] = self.buffer[index].start
            ex_mat[index][2] = self.buffer[index].end
            if (
                self.buffer[index].annotations is not None or
                len(self.buffer[index].annotations) is not 0
            ):
                self.create_anotation()
                ex_annotation[index] = self.get_annotation_tab(self.buffer[index])
        add_chunk(self, self.segments_nbr_in_chunk // CHUNK_SIZE + 1, ex_mat)
        if self.has_annotation():
            add_chunk(
                self,
                -(self.segments_nbr_in_chunk // CHUNK_SIZE + 1),
                ex_annotation
            )
        self.buffer = self.buffer[nbelement_to_store:]
        self.segments_nbr_in_chunk += nbelement_to_store

    def _sort(
            self
    ):
        """Returns a new segmentation with its segments sorted by (str_index,
        start, end) the original order is preserved for identical elements. To
        optimize, if the segmentation is already sorted, it doesn't copy it and
        just returns it.
        """

        sorted_keys = sorted(self.str_index_ptr.keys())
        already_sorted = True

        last = 0
        for k in sorted_keys:
            if self.str_index_ptr[k] < last:
                already_sorted = False
            last = self.str_index_ptr[k]

        if already_sorted:
            return self

        sorted_segmentation = Segmentation(label=self.label)
        for k in sorted_keys:
            i = self.str_index_ptr[k]
            segment = self[i]
            while segment.str_index == k:
                sorted_segmentation.append(segment)
                i += 1
                if i >= len(self):
                    # we reached the end of the segments list
                    break
                segment = self[i]

        return sorted_segmentation

    # TODO: update client code to match signature change (format=>formatting)
    def to_string(
        self,
        formatting=None,
        segment_delimiter='\n',
        header='',
        footer='',
        humanize_addresses=False,
        progress_callback=None,
        display_all=None,
    ):
        """Stringify a segmentation

        :param formatting: format string for each segment (default None)

        :param segment_delimiter: string inserted between consecutive segments
        (default '\n')

        :param header: string inserted at of output string (default
        '')

        :param footer: string inserted at end of output string (default '')

        :param humanize_addresses: boolean indicating whether string indices as
        well as start positions in strings should be numbered from 1, rather
        than from 0 as usual (default False)

        :param progress_callback: callback for monitoring progress ticks (number
        of input segments)

        :param display_all: parameter indicating whether the segmentation must
        be entirely stringified even though it is larger than
        MAX_SEGMENT_STRING; default is None = False.

        :return: formatted string

        In format string, it is possible to use the %(variable_name) format
        notation to insert variable element in each segment's formatted string,
        cf. https://orange-textable.readthedocs.org/en/latest/display.html.
        """

        if display_all is None:
            display_all = len(self) <= MAX_SEGMENT_STRING

        string = ''

        if display_all:

            string = header

            default_dict = None
            if formatting is not None:
                default_dict = dict(
                    (k, '__none__') for k in self.get_annotation_keys()
                )
                for match in re.finditer(r'(?<=%\()(.+?)(?=\))', formatting):
                    default_dict[match.group(0)] = '__none__'

            string += '\n'.join(
                [
                    segment.to_string(
                        formatting,
                        segment_delimiter,
                        humanize_addresses,
                        index+1,
                        default_dict,
                        progress_callback
                    )
                    for index, segment in enumerate(self)
                ]
            )

            string += footer

        else:

            string = header

            default_dict = None
            if formatting is not None:
                default_dict = dict(
                    (k, '__none__') for k in self.get_annotation_keys()
                )
                for match in re.finditer(r'(?<=%\()(.+?)(?=\))', formatting):
                    default_dict[match.group(0)] = '__none__'

            string += '\n'.join(
                [
                    self[index].to_string(
                        formatting,
                        segment_delimiter,
                        humanize_addresses,
                        index+1,
                        default_dict,
                        progress_callback
                    )
                    for index in range(min(len(self), NUM_SEGMENTS_SUMMARY))
                ]
            )

            string += '\n\n[%i segments not displayed...]\n\n' %  \
                      (len(self) - 2 * NUM_SEGMENTS_SUMMARY)

            string += '\n'.join(
                [
                    self[index].to_string(
                        formatting,
                        segment_delimiter,
                        humanize_addresses,
                        index+1,
                        default_dict,
                        progress_callback
                    )
                    for index in range(
                        max(len(self)-NUM_SEGMENTS_SUMMARY, 0),
                        len(self)
                    )
                ]
            )

            string += footer

        return string

    def to_html(
        self,
        humanize_addresses=False,
        progress_callback=None,
        display_all=None,
    ):
        """Stringify a segmentation in HTML format and returns an iterator.
        Useful when the actual string doesn't fit in memory.

        :param humanize_addresses: boolean indicating whether positions in
        strings should be numbered from 1, rather than from 0 as usual (default
        False)

        :param progress_callback: callback for monitoring progress ticks (number
        of input segments)

        :param display_all: parameter indicating whether the segmentation must
        be entirely stringified even though it is larger than
        MAX_SEGMENT_STRING; default is None = False.

        :return: a tuple containing the HTML formatted string and a boolean
        indicating whether it has been summarized or not.
        """

        # Summarize?
        if display_all is None:
            display_all = len(self) <= MAX_SEGMENT_STRING

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
        table_header = '<p><table class="textable">\n'
        wide_table_header = '<p><table class="textable" width="100%">\n'
        table_footer = '</table></p>\n'
        first_row_address = '<tr><th align="left">String index</th>' \
                            + '<th align="left">Start</th>' \
                            + '<th align="left">End</th></tr>\n'
        first_row_annotation = '<tr><th align="left">Annotation key</th>' \
                               + '<th align="left">Annotation value</th></tr>\n'
        first_row_content = '<tr><th align="left">Content</th></tr>\n'

        # Initializations...
        data = Segmentation.data
        counter = 1

        string = ''

        summarized = False

        if display_all:

            string = html_header
            string += '<h2>%s</h2>\n' % self.label

            string += '\n'.join(
                [
                    segment.to_html(
                        offset,
                        index+1,
                        table_header,
                        first_row_address,
                        first_row_annotation,
                        first_row_content,
                        wide_table_header,
                        table_footer,
                        progress_callback
                    )
                    for index, segment in enumerate(self)
                ]
            )
            string += html_footer

        else:

            summarized = True

            string = html_header
            string += '<h2>%s</h2>\n' % self.label

            string += '\n'.join(
                [
                    self[index].to_html(
                        offset,
                        index+1,
                        table_header,
                        first_row_address,
                        first_row_annotation,
                        first_row_content,
                        wide_table_header,
                        table_footer,
                        progress_callback
                    )
                    for index in range(min(len(self), NUM_SEGMENTS_SUMMARY))
                ]
            )

            string += '<p><i>[%i segments not displayed...]</i></p>' %  \
                      (len(self) - 2 * NUM_SEGMENTS_SUMMARY)

            string += '\n'.join(
                [
                    self[index].to_html(
                        offset,
                        index+1,
                        table_header,
                        first_row_address,
                        first_row_annotation,
                        first_row_content,
                        wide_table_header,
                        table_footer,
                        progress_callback
                    )
                    for index in range(
                        max(len(self) - NUM_SEGMENTS_SUMMARY, 0),
                        len(self)
                    )
                ]
            )

            string += html_footer

        return string, summarized

    def get_annotation_keys(self):
        """Get the list of available annotation keys"""

        # Initialize empty set.
        annotation_keys = set()

        # Take the union of each segment's annotation keys...
        for segment in self:
            annotation_keys = annotation_keys.union(
                list(segment.annotations)
            )

        return list(annotation_keys)

    def is_non_overlapping(self):
        """Determine if there is no segment overlap"""

        # Get list of segments sorted by address...
        segmentation_sorted = self._sort()

        # For each segment (but the last)...
        for first_index in range(len(segmentation_sorted) - 1):

            # Get the segment's address...
            first_segment = segmentation_sorted[first_index]
            first_str_index = first_segment.str_index
            first_string_length = len(Segmentation.data[first_str_index])
            first_end = first_segment.end or first_string_length

            # For each segment after this one...
            for second_index in range(first_index + 1, len(segmentation_sorted)):
                second_segment = segmentation_sorted[second_index]
                if second_segment.str_index != first_str_index:
                    continue
                if (second_segment.start or 0) < first_end:
                    return False

        return True
