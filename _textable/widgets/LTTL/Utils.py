#=============================================================================
# Module LTTL.Utils, v0.03
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
# Provides functions:
# - parse_xml_tag()
# - iround()
# - sample_dict()
# - get_variety()
# - get_average()
# - get_perplexity()
# - tuple_to_simple_dict()
# - get_unused_char_in_segmentation()
# - generate_random_annotation_key()
# - prepend_unit_with_category()
#=============================================================================

from __future__ import division
import re, random, math

from Segmentation import Segmentation
from Segment      import Segment
from Address      import Address

element_regex   = re.compile(r'(\w+)', re.U)
attribute_regex = re.compile(r'''(\w+)\s*=\s*['"](.+?)['"]''', re.U)


def parse_xml_tag(tag):
    """Parse an xml tag and return a dict describing it.

    The returned dict has the following keys:
    - is_element:   False for processing instructions, comments, etc.
    - is_opening:   True if tag is element opening tag, False otherwise
    - is_empty:     True if tag is empty element, False otherwise
    - element:      element name (None if not is_element)
    - attributes:   a dict with a key-value pair for each xml attribute

    If parsing failed somehow, return value is None.
    """
    tag_description = {
        'is_element':   False,
        'is_opening':   False,
        'is_empty':     False,
        'element':      None,
        'attributes':   {},
    }
    if tag[1] == '!' or tag[1] == '?':
        return tag_description
    elem = re.search(element_regex, tag)
    if elem:
        tag_description['is_element']       = True
        tag_description['element']          = elem.group(1)
        for attr in re.finditer(attribute_regex, tag):
            tag_description['attributes'][attr.group(1)] = attr.group(2)
        if tag[1] != '/':
            tag_description['is_opening']   = True
        elif tag[-2] == '/':
            tag_description['is_empty']     = True
        return tag_description
    return None
    

def iround(x):
    """Round a number to the nearest integer

    (from http://www.daniweb.com/software-development/python/threads/299459/
    round-to-nearest-integer)
    """
    return int(round(x) - .5) + (x > 0)
    

def sample_dict(
        dictionary,
        sample_size,
):
    """Return a randomly sampled frequency dict"""
    new_dict        = {}
    num_to_sample   = sample_size
    num_to_process  = sum(dictionary.itervalues())
    for (k, v) in dictionary.iteritems():
        for i in xrange(v):
            if random.random() < num_to_sample / num_to_process:
                new_dict[k] = new_dict.get(k, 0) + 1
                num_to_sample -= 1
            num_to_process -= 1
            if num_to_sample == 0:
                break
        else:
            continue
        break
    if num_to_sample > 0:
        raise ValueError(u'Not enough elements in dictionary')
    return new_dict


def get_variety(
        dictionary,
        unit_weighting      = False,
        category_weighting  = False,
        category_delimiter  = None,
):
    """Returns the variety/perplexity of items in a dictionary"""
    if category_delimiter is None:
        if unit_weighting:
            return get_perplexity(dictionary)
        else:
            return len(dictionary);
    else:
        category_dict = {}
        if not unit_weighting and not category_weighting:
            for (k, v) in dictionary.iteritems():
                (category, unit)        = k.split(category_delimiter, 1)
                category_dict[category] = category_dict.get(category, 0) + v
            return ( len(dictionary) / len(category_dict))
        else:
            units_in_category_dict  = {}
            unit_dict               = {}
            for (k, v) in dictionary.iteritems():
                (category, unit)        = k.split(category_delimiter, 1)
                category_dict[category] = category_dict.get(category, 0) + v
                units_in_category_dict[(category, unit,)] = (
                        units_in_category_dict.get((category, unit,), 0) + v
                )
                if unit_weighting:
                    unit_dict[k] = unit_dict.get(k, 0) + 1
            varieties = []
            weights   = []
            for category in category_dict.iterkeys():
                if category_weighting:
                    weights.append(category_dict[category])
                local_unit_dict = tuple_to_simple_dict(
                        units_in_category_dict,
                        category,
                )
                if unit_weighting:
                    varieties.append(get_perplexity(local_unit_dict))
                else:
                    varieties.append(len(local_unit_dict))
            if not category_weighting:
                weights = None
            (average, stdev) = get_average(varieties, weights)
            return average


def tuple_to_simple_dict(dictionary, key):
    """Take a dict with size-2 tuple key and a value for the 1st key element,
    and return a dict with only the 2nd key element as key.
    
    NB: keys with zero value are removed.
    """
    return {
            k[1]: v
                    for (k, v) in dictionary.iteritems()
                            if k[0] == key and v > 0
    }


def get_average(values, weights=None):
    """Compute the average and standard deviation of a list of values"""
    number_of_items = len(values)
    if number_of_items == 1:
        return (values[0], 0)
    sum_of_weights          = 0
    weighted_sum            = 0
    weighted_sum_squares    = 0
    for index in xrange(number_of_items):
        number = values[index]
        if weights:
            weight = weights[index]
        else:
            weight = 1
        sum_of_weights          += weight
        weighted_number          = weight * number
        weighted_sum            += weighted_number
        weighted_sum_squares    += weighted_number * number;
    average  = weighted_sum / sum_of_weights
    variance = weighted_sum_squares / sum_of_weights - average * average
    if variance < 0:
        variance = 0
    return (average, math.sqrt(variance))
    

def get_perplexity(dictionary):
    """Compute the perplexity (=exp entropy) of a dictionary"""
    sum                     = 0
    weighted_sum_of_logs    = 0
    for freq in dictionary.itervalues():
        if freq:
            sum                  += freq;
            weighted_sum_of_logs += freq * math.log(freq);
    return math.exp(math.log(sum) - weighted_sum_of_logs / sum);


def get_unused_char_in_segmentation(segmentation, annotation_key=None):
    """Return a unicode character that does NOT appear in segmentation"""
    global_max = 0
    for segment in segmentation:
        if annotation_key:
            text = segment.annotations.get(
                    annotation_key,
                    u'__none__',
            )
        else:
            text = segment.get_content()
        local_max = max(ord(c) for c in text)
        if local_max > global_max:
            global_max = local_max
    return unichr(global_max+1)


def prepend_unit_with_category(
        segmentation,
        category_delimiter,
        new_annotation_key,
        category_annotation_key,
        unit_annotation_key     = None,
):
    """Copy segmentation, creating a new annotation key whose values are
    segment contents or annotation values prepended with another annotation
    value.
    """
    new_segments = []
    for segment in segmentation:
        new_segments.append(Segment(
                Address(
                        segment.address.str_index,
                        segment.address.start,
                        segment.address.end,
                ),
                segment.annotations.copy()
        ))
        if unit_annotation_key:
            unit = segment.annotations.get(unit_annotation_key, u'__none__')
        else:
            unit = segment.get_content()
        if category_annotation_key:
            category = segment.annotations.get(
                    category_annotation_key, u'__none__'
            )
        else:
            category = segment.get_content()
        new_segments[-1].annotations[new_annotation_key] = (
                category_delimiter.join([category, unit])
        )
    return Segmentation(new_segments, segmentation.label)


def generate_random_annotation_key(segmentation, length=8):
    existing_keys = segmentation.get_annotation_keys()
    while True:
        new_key = ''.join(random.choice('01.3456789') for x in range(length))
        if new_key not in existing_keys:
            break
    return new_key



if __name__ == '__main__':
    from Segmenter import Segmenter
    from Input     import Input
    test_tags = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<a b="1" c="2">',
        '</d>',
        '<empty/>',
    ]
    for test_tag in test_tags:
        print test_tag
        tag_description = parse_xml_tag(test_tag)
        if tag_description:
            for (k, v) in tag_description.items():
                print '%-15s: %s' % (k, v)
        else:
            print 'parsing failed'
    my_dict = {'a':2, 'b':1, 'c':1}
    for i in range(10):
        print sample_dict(my_dict, 2)
    try:
        sample_dict(my_dict, 5)
    except ValueError:
        print "exception correctly raised"
    my_dict = {('a','A'): 1, ('a','B'): 2, ('b','A'): 0, ('b','B'): 3}
    print tuple_to_simple_dict(my_dict, 'a')
    print tuple_to_simple_dict(my_dict, 'b')
    values  = [2, 3, 4]
    weights = [2, 1, 1]
    print get_average(values)
    print get_average(values, weights)
    print get_perplexity({'a': 1, 'b': 1})
    unit_dict          = {'a':1, 'b': 2}
    category_dict      = {'A':2, 'B': 1}
    recoded_unit_dict  = {'A#a':1, 'A#b': 1, 'B#b':1}
    print get_variety(unit_dict)
    print get_variety(unit_dict, unit_weighting=1)
    print get_variety(recoded_unit_dict, category_delimiter='#')
    print get_variety(
            recoded_unit_dict,
            unit_weighting      = 1,
            category_delimiter  = '#'
    )
    print get_variety(
            recoded_unit_dict,
            category_weighting  = 1,
            category_delimiter  = '#',
    )
    print get_variety(
            recoded_unit_dict,
            unit_weighting      = 1,
            category_weighting  = 1,
            category_delimiter  = '#',
    )
    print generate_random_dict_key(recoded_unit_dict, length=8)
    seg1 = Input(u'hello world', 'text1')
    seg2 = Input(u'cruel world', 'text2')
    segmenter = Segmenter()
    seg3 = segmenter.concatenate([seg1, seg2], 'corpus')
    print prepend_unit_with_category(
        seg3,
        get_unused_char_in_segmentation(seg3, 'component_label'),
        generate_random_dict_key(recoded_unit_dict, length=8),
        'component_label',
        unit_annotation_key     = None,
    ).to_string()

