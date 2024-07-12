.. meta::
   :description: Orange Textable documentation, count transition frequency 
                 between adjacent units 
   :keywords: Orange, Textable, documentation, cookbook, count, transition, 
              frequency, Markov Chain

Count transition frequency between adjacent units 
=================================================

Goal
----

Count the frequency of transitions between adjacent segment types in a text.

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and it has been segmented in smaller units
(see :doc:`Cookbook: Segment text in smaller units <segment_text>`).

Ingredients
-----------

  ==============  =======
   **Widget**      :ref:`Count`
   **Icon**        |count_icon|
   **Quantity**    1
  ==============  =======

.. |count_icon| image:: figures/Count_36.png


Procedure
---------

.. _count_transition_frequency_between_adjacent_units_fig1:

.. figure:: figures/count_frequency_adjacent_contexts.png
   :align: center
   :alt: Count frequency of adjacent contexts with an instance of Count

   Figure 1: Count transition frequency with an instance of :ref:`Count`

1. Create an instance of :ref:`Count` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that has been used to segment the text (e.g. :ref:`Segment`) to
   the :ref:`Count` widget instance's input connection (lefthand side).
3. Open the :ref:`Count` instance's interface by double-clicking on its
   icon on the canvas.
4. In the **Units** section, select the segmentation in which transitions
   between units will be counted.
5. In the **Context** section, choose **Mode: Left-right neighborhood**.
6. Select **Left context size:** *1* and **Right context size:** *0*.
7. Click the **Compute** button (or make sure the **Compute automatically**
   checkbox is selected).
8. A table showing the results is then available at the output connection of
   the :ref:`Count` instance; to display or export it, see :ref:`Cookbook:
   Table output <cookbook_toc_table_output_ref>`.

  
Comment
-------
* It is also possible to define units as segment pairs (*bigrams*), triples
  (*trigrams*), and so on, by increasing the **Sequence length** parameter in
  the **Units** section.
* If **Sequence length** is set to a value greater than 1, the string
  appearing in the **Intra-sequence delimiter** field will be inserted between
  the elements composing each *n*-gram in the column headers, which can
  enhance their readability. The default is ``#`` but you can change it by
  inserting the delimiter of your choice.
* Furthermore, it is possible to count the apparition of units in more complex
  contexts than simply the previous unit, such as: the *n* previous units
  (**Left context size**); the *n* following units (**Right context size**);
  or any combination of both.
* The **Unit position marker** is a string that indicates the separation
  between left and right contexts sides. The default is ``_`` but you can
  change it by inserting the marker of your choice.

See also
--------

* :ref:`Reference: Count widget <Count>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :doc:`Cookbook: Segment text in smaller units <segment_text>`
* :ref:`Cookbook: Table output <cookbook_toc_table_output_ref>`

