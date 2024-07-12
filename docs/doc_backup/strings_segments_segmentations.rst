.. meta::
   :description: Orange Textable documentation, strings, segments, and
                 segmentation
   :keywords: Orange, Textable, documentation, strings, segments, segmentation

Strings, segments, and segmentations
====================================

The main purpose of Orange Textable is to build tables based on text strings.
As we will see, there are several methods for importing text strings, the
simplest of which is keyboard input using widget
:ref:`Text Field` (see also :doc:`Keyboard input and segmentation
display <keyboard_input_segmentation_display>` or 
:doc:`Cookbook: Import text from keyboard <import_text_keyboard>`.
Whenever a new string is imported, it is assigned a unique identification number 
(called *string index*) and stays in memory as long as the widget that imported 
it.

Consider the following string of 16 characters (note that whitespace counts as
a character too), and let us suppose that its string index is 1:

.. csv-table::
    :stub-columns: 1
    :widths: 10 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3

    "Character", *a*, " ", *s*, *i*, *m*, *p*, *l*, *e*, " ", *e*, *x*, *a*, *m*, *p*, *l*, *e*
    "Position", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,16

In this context, a *segment* is basically a substring of characters. Every
segment has an *address* consisting of three elements:

    1. string index
    2. initial position within the string
    3. final position

In the case of *a simple example*, address (1, 3, 8) refers to substring
*simple*, (1, 12, 12) to character *a*, and (1, 1, 16) to the entire string.
The substring corresponding to a given address is called the segment's
*content*.

A *segmentation* is an ordered list of segments. For instance, segmentation
((1, 1, 1 ), (1, 3, 8), (1, 10, 16)) contains 3 word segments, ((1, 1, 1),
(1, 2, 2 ), ..., (1, 16, 16)) contains 16 character segments, and ((1, 1, 16))
contains a single segment covering the whole string.

As shown by the word segmentation example, every character in the string needs
not be included in a segment. Moreover, a single character may belong to
several segments simultaneously, as in ((1, 1, 1), (1, 1, 8), (1, 3, 8),
(1, 3, 16), (1, 10, 16)). 

.. _string_segments_segmentations_ex1:

**Exercise 1:** What is the content of each of the 5 segments in the previous
example? (:ref:`solution <solution_string_segments_segmentations_ex1>`)

**NB, new in version 2.0 and later:** The order of segments in a segmentation 
must be the same as the order of the corresponding substrings in the string.
For instance ((1, 1, 1), (1, 2, 1), (1, 2, 2)) is possible, but not ((1, 2, 1), 
(1, 1, 1)), because the second segment starts before the first. Similarly, 
((1, 2, 2), (1, 2, 1)) isn't possible because the second segment ends before
the first.

In the previous examples, all the segments of a given segmentation refer to
the same string. However, a segmentation may contain segments belonging to
several distinct strings. Thus, if string *another example* has string index
2, segmentation ((2, 1, 7), (1, 3, 16)) is perfectly valid.

.. _string_segments_segmentations_ex2:

**Exercise 2:** What is the content of the segments in the previous
example? (:ref:`solution <solution_string_segments_segmentations_ex2>`)

**NB, new in version 2.0 and later:** In a single segmentation, two segment
that have the same string index cannot be separated by a segment with a different
string index. For instance ((**1**, 1, 1), (**2**, 1, 1), (**2**, 2, 1)) is 
possible, but not ((**2**, 1, 1), (**1**, 1, 1), (**2**, 2, 1)).

In order to store segmentations and transmit them between widgets, Orange
Textable uses the *Segmentation* data type. Aside from the segment addresses,
this data type associates a *label* with each segmentation, i.e. an arbitrary
string used to identify the segmentation among others. [#]_

.. _solution_string_segments_segmentations_ex1:

**Solution to exercise 1:** *a*, *a simple*, *simple*, *simple example*, *example*
(in this order).
(:ref:`back to the exercise <string_segments_segmentations_ex1>`)

.. _solution_string_segments_segmentations_ex2:

**Solution to exercise 2:** *another*, *simple example*.
(:ref:`back to the exercise <string_segments_segmentations_ex2>`)

.. [#] As we will see :doc:`later <annotations>`, the *Segmentation* data type
       can also store annotations associated with segments.


See also
--------

* :doc:`Getting started: Keyboard input and segmentation display
  <keyboard_input_segmentation_display>`
* :doc:`Cookbook: Import text from keyboard <import_text_keyboard>`
