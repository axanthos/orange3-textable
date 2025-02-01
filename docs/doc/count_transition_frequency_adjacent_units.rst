Count transition frequency between adjacent units
======================================================

Goal
--------

Count the frequency of transitions between adjacent segment types in a
text.

Prerequisites
-----------------

Some text has been imported in Orange Textable (see :doc:`Cookbook: Text input <text_input>`)
and it has been segmented in smaller units (see :doc:`Cookbook: Segment text in smaller units <segment_text>`).

Ingredients
---------------

  ==============  =======
   **Widget**      :doc:`Count <count>`
   **Icon**        |count_icon|
   **Quantity**    1
  ==============  =======

.. |count_icon| image:: figures/Count_36.png

Procedure
-------------

.. _count_transition_frequency_between_adjacent_units_fig1:

.. figure:: figures/count_frequency_adjacent_contexts.png
   :align: center
   :alt: Count frequency of adjacent contexts with an instance of Count

   Figure 1: Count transition frequency with an instance of :doc:`Count <count>`

1. Create an instance of
   :doc:`Count <count>`.

2. Drag and drop from the output (righthand side) of the widget that has
   been used to segment the text, here
   :doc:`Segment <segment>`
   (*letters*), to the input of
   :doc:`Count <count>`
   (lefthand side).

3. Double-click on the icon of
   :doc:`Count <count>`
   to open its interface.

4. In the **Units** section, select the segmentation in which
   transitions between units will be counted (here *letters*).

5. In the **Context** section, choose **Mode: Left-right neighborhood**.

6. Select **Left context size:** *1* and **Right context size:** *0*.

7. Click the **Send** button or tick the **Send automatically**
   checkbox.

8. A table showing the results is then available at the output of
   :doc:`Count <count>`;
   to display or export it, see :doc:`Cookbook: Table output <table_output>`.

Comment
-----------

-  It is also possible to define units as segment pairs (*bigrams*),
   triples (*trigrams*), and so on, by increasing the **Sequence
   length** parameter in the **Units** section.

-  If **Sequence length** is set to a value greater than 1, the string
   appearing in the **Intra-sequence delimiter** field will be inserted
   between the elements composing each *n*-gram in the column headers,
   which can enhance their readability. The default is ``#`` but you can
   change it to the delimiter of your choice.

-  Furthermore, it is possible to count the apparition of units in more
   complex contexts than simply the previous unit, such as: the *n*
   previous units (**Left context size**); the *n* following units
   (**Right context size**); or any combination of both.

-  The **Unit position marker** is a string that indicates the
   separation between left and right contexts sides. The default is ``_``
   but you can change it to the marker of your choice.

See also
------------

-  :doc:`Reference: Count widget <count>`
-  :doc:`Cookbook: Text input <text_input>`
-  :doc:`Cookbook: Segment text in smaller units <segment_text>`
-  :doc:`Cookbook: Table output <table_output>`