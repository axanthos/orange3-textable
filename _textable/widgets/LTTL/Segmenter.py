#=============================================================================
# Class LTTL.Segmenter, v0.22
# Copyright 2012-2015 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the LTTL package v1.5
#
# LTTL v1.5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LTTL v1.5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LTTL v1.5. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

from __future__ import division

import re, random

from Segmentation import Segmentation
from Address      import Address
from Segment      import Segment

from Utils        import parse_xml_tag, iround

class Segmenter(object):

    """A class to produce a new segmentation based on existing one(s)."""

    def concatenate(
            self,
            segmentations,
            label               = u'my_concatenation',
            copy_annotations    = True,
            import_labels_as    = u'component_label',
            auto_numbering_as   = None,
            sort                = False,
            merge_duplicates    = False,
            progress_callback   = None,
    ):

        """Take a list of segmentations and produce a concatenation"""

        # Copy input segmentations...
        new_segments = []
        append_to_new_segments = new_segments.append
        for segmentation in segmentations:
            for segment in segmentation:
                existing_address = segment.address
                new_address = Address(
                        existing_address.str_index,
                        existing_address.start,
                        existing_address.end,
                )
                new_annotations = {}
                if copy_annotations:
                    new_annotations = segment.annotations.copy()
                if (
                        import_labels_as is not None
                    and len(import_labels_as) > 0
                ):
                    new_annotations[import_labels_as] = segmentation.label
                append_to_new_segments(Segment(new_address, new_annotations))
                if progress_callback:
                    progress_callback()

        # Sort output segment list...
        if sort:
            new_segments.sort(key=lambda s: (
                    s.address.str_index,
                    s.address.start,
                    s.address.end,
            ))

        # Delete duplicate segments and merge their annotations...
        if merge_duplicates:
            new_segments = Segmenter.merge_duplicate_segments(
                    new_segments,
                    progress_callback,
            )

        # Auto-numbering...
        if (auto_numbering_as is not None and len(auto_numbering_as) > 0):
            Segmenter.auto_number(
                    new_segments,
                    auto_numbering_as,
                    progress_callback,
            )

        # Create and return new segmentation
        return Segmentation(new_segments, label)


    def tokenize(
            self,
            segmentation,
            regexes,
            label               = u'my_segmented_data',
            import_annotations  = True,
            merge_duplicates    = True,
            auto_numbering_as   = None,
            progress_callback   = None,
    ):

        """Create a tokenized segmentation based on an existing one.

        Arg regexes is a list of tuple, where each tuple has a compiled regex
        as first element, either u'Tokenize' or u'Split' as second element,
        and an optional dict as third element; the dict has a single key
        representing an annotation key to be created with the corresponding
        value; regexes are successively applied to each segment of the input
        segmentation.

        Only in u'Tokenize' mode:
        Annotation keys and values may contain backreferences in the form of
        and ampersand (&) immediately followed by a digit referring to the
        group to be captured. E.g. if the regex is r'Mrs? ([A-Z]\w+)', the
        annotation key--value pair could be {'name': '&1'}, so that the name
        is actually captured in the annotation.
        """

        new_segmentation = Segmentation([], label)

        # Prepare formats for annotations keys and values if necessary...
        annotation_key_backref_indices   = []
        annotation_value_backref_indices = []
        annotation_key_format            = []
        annotation_value_format          = []
        contains_backrefs = re.compile(r'&([0-9]+)')
        for regex in regexes:
            if len(regex) == 3:
                key   = regex[2].keys()[0]
                value = regex[2].values()[0]
                annotation_key_backref_indices.append([
                    match for match in contains_backrefs.findall(key)
                ])
                annotation_value_backref_indices.append([
                    match for match in contains_backrefs.findall(value)
                ])
                if len(annotation_key_backref_indices[-1]):
                    annotation_key_format.append(
                            contains_backrefs.sub(u'%s', key)
                    )
                else:
                    annotation_key_format.append(None)
                if len(annotation_value_backref_indices[-1]):
                    annotation_value_format.append(
                            contains_backrefs.sub(u'%s', value)
                    )
                else:
                    annotation_value_format.append(None)
            else:
                annotation_key_backref_indices.append([])
                annotation_value_backref_indices.append([])
                annotation_key_format.append(None)
                annotation_value_format.append(None)

        # Perform tokenization...
        for segment in segmentation:
            new_segments    = []
            old_segment_annotation_copy = {}
            if import_annotations:
                old_segment_annotation_copy = segment.annotations.copy()
            str_index   = segment.address.str_index
            start_pos   = segment.address.start or 0
            content     = segment.get_content()
            for regex_index in range(len(regexes)):
                regex = regexes[regex_index]
                regex_annotations = old_segment_annotation_copy.copy()
                if regex[1] == u'Tokenize':
                    for m in re.finditer(regex[0], content):
                        key   = None
                        value = None
                        if len(annotation_key_backref_indices[regex_index]):
                            key = annotation_key_format[regex_index] % tuple([
                                m.group(int(i))
                                    for i in annotation_key_backref_indices[
                                        regex_index
                                    ]
                            ])
                        elif len(regex) == 3:
                            key = regex[2].keys()[0]
                        if len(annotation_value_backref_indices[regex_index]):
                            value = annotation_value_format[
                                regex_index
                            ] % tuple([
                                m.group(int(i))
                                    for i in annotation_value_backref_indices[
                                        regex_index
                                    ]
                            ])
                        elif len(regex) == 3:
                            value = regex[2].values()[0]
                        new_segment_annotations = regex_annotations.copy()
                        if key is not None and value is not None:
                            new_segment_annotations.update({key: value})
                        new_segments.append(
                                Segment(
                                        Address(
                                                str_index,
                                                start_pos + m.start(),
                                                start_pos + m.end(),
                                        ),
                                        new_segment_annotations
                                )
                        )
                else:
                    new_segment_annotations = regex_annotations.copy()
                    if len(regex) == 3:
                        key   = regex[2].keys()[0]
                        value = regex[2].values()[0]
                        new_segment_annotations.update({key: value})
                    previous_end_pos = start_pos
                    for m in re.finditer(regex[0], content):
                        if start_pos + m.start() == previous_end_pos:
                            previous_end_pos = start_pos + m.end()
                            continue
                        new_segments.append(
                                Segment(
                                        Address(
                                                str_index,
                                                previous_end_pos,
                                                start_pos + m.start(),
                                        ),
                                        new_segment_annotations.copy()
                                )
                        )
                        previous_end_pos = start_pos + m.end()
                    segment_end_pos = start_pos + len(content)
                    if previous_end_pos < segment_end_pos:
                        new_segments.append(
                                Segment(
                                        Address(
                                                str_index,
                                                previous_end_pos,
                                                segment_end_pos,
                                        ),
                                        new_segment_annotations.copy()
                                )
                        )
                # Sort segments...
                new_segments.sort(key=lambda s: (
                        s.address.str_index,
                        s.address.start,
                        s.address.end,
                ))

                # Merge duplicate segments...
                if merge_duplicates:
                    new_segments = Segmenter.merge_duplicate_segments(
                            new_segments,
                    )

                if progress_callback:
                    progress_callback()

            new_segmentation.segments.extend(new_segments)

        # Auto-numbering...
        if (auto_numbering_as is not None and len(auto_numbering_as) > 0):
            Segmenter.auto_number(
                    new_segmentation.segments,
                    auto_numbering_as,
            )
        return new_segmentation


    def select(
            self,
            segmentation,
            regex,
            mode                = 'include',
            annotation_key      = None,
            label               = u'my_selected_data',
            copy_annotations    = True,
            auto_numbering_as   = None,
            progress_callback   = None,
    ):
        """In-/exclude segments in a segmentation based on a regex."""
        new_segmentation = Segmentation([], label)
        neg_segmentation = Segmentation([], u'NEG_' + label)
        for segment in segmentation:
            old_segment_annotation_copy = {}
            if copy_annotations:
                old_segment_annotation_copy = segment.annotations.copy()
            if annotation_key:
                if annotation_key in segment.annotations:
                    match = regex.search(
                        unicode(segment.annotations[annotation_key])
                    )
                else:
                    match = None
            else:
                match = regex.search(segment.get_content())
            address = segment.address
            new_segment = Segment(
                    Address(
                            address.str_index,
                            address.start,
                            address.end,
                    ),
                    old_segment_annotation_copy
            )
            if (
                    (    match and mode == 'include')
                 or (not match and mode == 'exclude')
            ):
                new_segmentation.segments.append(new_segment)
            else:
                neg_segmentation.segments.append(new_segment)
            if progress_callback:
                progress_callback()
        if (auto_numbering_as is not None and len(auto_numbering_as) > 0):
            Segmenter.auto_number(
                    new_segmentation.segments,
                    auto_numbering_as,
            )
            Segmenter.auto_number(
                    neg_segmentation.segments,
                    auto_numbering_as,
            )
        return (new_segmentation, neg_segmentation)


    def threshold(
            self,
            segmentation,
            min_count           = None,
            max_count           = None,
            annotation_key      = None,
            label               = u'my_thresholded_data',
            copy_annotations    = True,
            auto_numbering_as   = None,
            progress_callback   = None,
    ):

        """Include segments in a segmentation based on min/max count."""

        if min_count is None:
            min_count = 0
        if max_count is None:
            max_count = len(segmentation)

        # Get type counts...
        if annotation_key is not None:
            type_list = [
                    u.annotations[annotation_key]
                        for u in segmentation
                            if annotation_key in u.annotations
            ]
        else:
            type_list = [
                    u.get_content() for u in segmentation
            ]
        type_counts = {}
        for my_type in type_list:
            type_counts[my_type] = type_counts.get(my_type, 0) + 1

        # Perform the actual thresholding...
        new_segmentation = Segmentation([], label)
        neg_segmentation = Segmentation([], u'NEG_' + label)
        for segment in segmentation:
            old_segment_annotation_copy = {}
            if copy_annotations:
                old_segment_annotation_copy = segment.annotations.copy()
            if annotation_key:
                my_type = segment.annotations[annotation_key]
            else:
                my_type = segment.get_content()
            address = segment.address
            new_segment = Segment(
                    Address(
                            address.str_index,
                            address.start,
                            address.end,
                    ),
                    old_segment_annotation_copy
            )
            if (
                    type_counts[my_type] >= min_count
                and type_counts[my_type] <= max_count
            ):
                new_segmentation.segments.append(new_segment)
            else:
                neg_segmentation.segments.append(new_segment)
            if progress_callback:
                progress_callback()
        if (auto_numbering_as is not None and len(auto_numbering_as) > 0):
            Segmenter.auto_number(
                    new_segmentation.segments,
                    auto_numbering_as,
            )
            Segmenter.auto_number(
                    neg_segmentation.segments,
                    auto_numbering_as,
            )
        return (new_segmentation, neg_segmentation)


    def sample(
            self,
            segmentation,
            sample_size,
            mode                = 'random',
            label               = u'my_sampled_data',
            copy_annotations    = True,
            auto_numbering_as   = None,
            progress_callback   = None,
    ):
        """Sample a segmentation"""
        new_segmentation = Segmentation([], label)
        neg_segmentation = Segmentation([], u'NEG_' + label)
        if mode == 'random':
            sampled_indices = sorted(random.sample(
                    xrange(len(segmentation)),
                    sample_size
            ))
        elif mode == 'systematic':
            step            = iround(1 / (sample_size / len(segmentation)))
            sampled_indices = range(len(segmentation))[::step]
        for segment_index in xrange(len(segmentation)):
            segment = segmentation.segments[segment_index]
            old_segment_annotation_copy = {}
            if copy_annotations:
                old_segment_annotation_copy = segment.annotations.copy()
            address = segment.address
            new_segment = Segment(
                    Address(
                            address.str_index,
                            address.start,
                            address.end,
                    ),
                    old_segment_annotation_copy
            )
            if segment_index in sampled_indices:
                new_segmentation.segments.append(new_segment)
            else:
                neg_segmentation.segments.append(new_segment)
            if progress_callback:
                progress_callback()
        if (auto_numbering_as is not None and len(auto_numbering_as) > 0):
            Segmenter.auto_number(
                    new_segmentation.segments,
                    auto_numbering_as,
            )
            Segmenter.auto_number(
                    neg_segmentation.segments,
                    auto_numbering_as,
            )
        return (new_segmentation, neg_segmentation)


    def intersect(
            self,
            source,
            filtering,
            mode                = 'include',
            label               = u'my_selected_data',
            copy_annotations    = True,
            auto_numbering_as   = None,
            progress_callback   = None,
    ):
        """In-/exclude segments in a segmentation based on types in another
        segmentation.

        Parameter source is a dict with the following keys and values:
        KEY                     VALUE                           DEFAULT
        segmentation            source segmentation             None
        annotation_key          annotation key to be used       None

        Parameter filtering is a dict with the following keys and values:
        KEY                     VALUE                           DEFAULT
        segmentation            filtering segmentation          None
        annotation_key          annotation key to be used       None
        """

        default_source = {
                'segmentation':     None,
                'annotation_key':   None,
        }
        default_filtering = {
                'segmentation':     None,
                'annotation_key':   None,
        }
        if source is not None:
            default_source.update(source)
        source = default_source
        if filtering is not None:
            default_filtering.update(filtering)
        filtering = default_filtering

        # Get the dict of filtering types...
        filtering_annotation_key = filtering['annotation_key']
        if filtering_annotation_key is not None:
            type_list = [
                    u.annotations[filtering_annotation_key]
                        for u in filtering['segmentation']
                            if filtering_annotation_key in u.annotations
            ]
        else:
            type_list = [
                    u.get_content() for u in filtering['segmentation']
            ]
        type_dict = {}
        for my_type in type_list:
            type_dict[my_type] = 1

        # Perform the actual 'intersection'
        new_segmentation = Segmentation([], label)
        neg_segmentation = Segmentation([], u'NEG_' + label)
        source_annotation_key = source['annotation_key']
        for segment in source['segmentation']:
            old_segment_annotation_copy = {}
            if copy_annotations:
                old_segment_annotation_copy = segment.annotations.copy()
            if source_annotation_key:
                match = unicode(segment.annotations[source_annotation_key]) \
                                in type_dict
            else:
                match = segment.get_content() in type_dict
            address = segment.address
            new_segment = Segment(
                    Address(
                            address.str_index,
                            address.start,
                            address.end,
                    ),
                    old_segment_annotation_copy
            )
            if (
                    (    match and mode == 'include')
                 or (not match and mode == 'exclude')
            ):
                new_segmentation.segments.append(new_segment)
            else:
                neg_segmentation.segments.append(new_segment)
            if progress_callback:
                progress_callback()

        if (auto_numbering_as is not None and len(auto_numbering_as) > 0):
            Segmenter.auto_number(
                    new_segmentation.segments,
                    auto_numbering_as,
            )
            Segmenter.auto_number(
                    neg_segmentation.segments,
                    auto_numbering_as,
            )
        return (new_segmentation, neg_segmentation)


    def import_xml(
            self,
            segmentation,
            element,
            conditions          = None,
            import_element_as   = u'__xml_element__',
            label               = u'my_xml_data',
            import_annotations  = True,
            remove_markup       = True,
            auto_numbering_as   = None,
            merge_duplicates    = False,
            preserve_leaves     = False,
            progress_callback   = None,
    ):

        """Create a segmentation based on the xml content of an existing one.
        
        Arg. 'conditions' is a dict where each key is the name of an attribute
        and each value is a compiled regex that must be satisfied by the
        attribute value for an element to be selected.

        XML processing is rather crude for the time being: no attempt to
        resolve entities, detect errors and recover from them, and so on.
        """

        if conditions is None:
            conditions = {}
        tag_regex       = re.compile(r'<.+?>')
        data            = Segmentation.data
        stack           = []
        attr_stack      = []
        new_segments    = []

        for old_segment in segmentation:
            old_content = old_segment.get_content()
            old_anno_copy = {}
            if import_annotations:
                old_anno_copy = old_segment.annotations.copy()
            if (import_element_as is not None and len(import_element_as) > 0):
                old_anno_copy.update({
                    import_element_as: element
                })
            old_address   = old_segment.address
            old_str_index = old_address.str_index
            old_start     = old_address.start or 0
            for match in re.finditer(tag_regex, old_content):
                tag_start = old_start + match.start()
                tag_end   = old_start + match.end()
                tag       = data[old_str_index][tag_start:tag_end]
                tag_desc  = parse_xml_tag(tag)

                if remove_markup:
                    for index in xrange(len(stack)):
                        if stack[index][-1][0] == old_str_index:
                            stack[index][-1][2] = tag_start
                        else:
                            anno = old_anno_copy.copy()
                            anno.update(attr_stack[index])
                            stack[index].append(
                                    [old_str_index, 0, tag_start, anno]
                            )
                    if tag_desc['element'] == element:
                        if (
                                tag_desc['is_opening'] == True
                            and tag_desc['is_empty']   == False
                        ):
                            stack.append([])
                            attr_stack.append(tag_desc['attributes'])
                        elif stack:
                            new_segments.extend(stack.pop())
                            attr_stack.pop()
                    for index in xrange(len(stack)):
                        anno = old_anno_copy.copy()
                        anno.update(attr_stack[index])
                        stack[index].append(
                                [old_str_index, tag_end, None, anno]
                        )
                else:
                    for index in xrange(len(stack)):
                        if stack[index][-1][0] != old_str_index:
                            anno = old_anno_copy.copy()
                            anno.update(attr_stack[index])
                            stack[index].append(
                                    [old_str_index, 0, None, anno]
                            )
                    if tag_desc['element'] == element:
                        if (
                                tag_desc['is_opening'] == True
                            and tag_desc['is_empty']   == False
                        ):
                            anno = old_anno_copy.copy()
                            anno.update(tag_desc['attributes'])
                            stack.append([
                                    [old_str_index, tag_end, None, anno]
                            ])
                            attr_stack.append(tag_desc['attributes'])
                        elif stack:
                            stack[-1][-1][2] = tag_start
                            new_segments.extend(stack.pop())

            if progress_callback:
                progress_callback()

        if stack: raise ValueError(u'xml parsing error')

        new_segments = [
                Segment(Address(s[0], s[1], s[2]), s[3]) for s in new_segments
        ]
        if preserve_leaves:
            new_segments.reverse()

        # Remove segments that are empty or don't match attribute regexes...
        for index in reversed(range(len(new_segments))):
            segment = new_segments[index]
            address = segment.address
            start   = address.start or 0
            end     = address.end or len(Segmentation.data[address.str_index])
            if start == end:
                new_segments.pop(index)
                continue
            annotations = segment.annotations
            for (attr, value_regex) in conditions.items():
                if (
                    (not attr in annotations)
                    or
                    (not value_regex.search(annotations[attr]))
                ):
                    new_segments.pop(index)
                    break

        # Sort segments...
        new_segments.sort(key=lambda s: (
                s.address.str_index,
                s.address.start,
                s.address.end,
        ))

        # Delete duplicate segments and merge their annotations...
        if merge_duplicates:
            new_segments = Segmenter.merge_duplicate_segments(
                    new_segments,
            )

        new_segmentation = Segmentation([], label)
        new_segmentation.segments.extend(new_segments)

        # Auto-numbering...
        if (auto_numbering_as is not None and len(auto_numbering_as) > 0):
            Segmenter.auto_number(
                    new_segmentation.segments,
                    auto_numbering_as,
            )
        return new_segmentation


    def bypass(
            self,
            segmentation,
            label           = u'my_bypassed_data',
    ):
        """Return a verbatim copy of a segmentation"""
        new_segmentation = Segmentation([], label)
        neg_segmentation = Segmentation([], u'NEG_' + label)
        new_segmentation.segments.extend(
                [
                        Segment(
                                Address(
                                        s.address.str_index,
                                        s.address.start,
                                        s.address.end,
                                ),
                                s.annotations.copy()
                        )
                                for s in segmentation.segments
                ]
        )
        return (new_segmentation, neg_segmentation)


    @staticmethod
    def merge_duplicate_segments(segment_list, progress_callback=None):
        """Delete duplicate segments in a list and merge their annotations

        Although this has been optimized, it is still very slow for large
        segment lists...
        """
        index = 0
        while index < len(segment_list):
            segment     = segment_list[index]
            address     = segment.address
            str_index   = address.str_index
            start       = address.start or 0
            text_length = len(Segmentation.data[str_index])
            end         = address.end or text_length
            to_delete = [
                    s for s in segment_list[index+1:]
                            if (
                                   str_index ==  s.address.str_index
                               and start     == (s.address.start or 0)
                               and end       == (s.address.end or text_length)
                            )
            ]
            segment_update = segment.annotations.update
            for duplicate in to_delete:
                segment_update(duplicate.annotations)
            segment_list = [s for s in segment_list if s not in to_delete]
            index += 1
            if progress_callback:
                progress_callback()
        return segment_list


    @staticmethod
    def auto_number(segment_list, annotation_key, progress_callback=None):
        """Add annotation with integers from 1 to N to segments in a list"""
        counter = 1
        for segment in segment_list:
            segment.annotations[annotation_key] = counter
            counter += 1
            if progress_callback:
                progress_callback()


