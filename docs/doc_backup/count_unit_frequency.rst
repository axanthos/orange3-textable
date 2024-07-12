.. meta::
   :description: Orange Textable documentation, cookbook, count unit frequency
   :keywords: Orange, Textable, documentation, cookbook, count, unit,
              frequency, distribution
   
   
Count unit frequency
====================

Goal
----

Count the frequency of each segment type that appears in a segmentation.

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

.. _count_unit_frequency_fig1:

.. figure:: figures/count_unit_fequency_globally.png
   :align: center
   :alt: Count unit frequency globally with an instance of Count

   Figure 1: Count unit frequency globally with an instance of :ref:`Count`.
   
 
1. Create an instance of :ref:`Count` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segments that will be counted (e.g. :ref:`Segment`)
   to the :ref:`Count` widget instance's input connection (lefthand side).
3. Open the :ref:`Count` instance's interface by double-clicking on its
   icon on the canvas.
4. In the **Units** section, select the segmentation containing units to be
   counted in the **Segmentation** drop-down menu (here: *letters*).
5. Click the **Compute** button (or make sure the **Compute automatically**
   checkbox is selected).
6. A table showing the results is then available at the output connection of
   the :ref:`Count` instance; to display or export it, see :ref:`Cookbook:
   Table output <cookbook_toc_table_output_ref>`.

Comment
-------
* The total number of segments in your segmentation appears in the **Info**
  section (here: 14).
* It is also possible to define units as segment pairs (*bigrams*), triples
  (*trigrams*), and so on, by increasing the **Sequence length** parameter in
  the **Units** section.
* If **Sequence length** is set to a value greater than 1, the string
  appearing in the **Intra-sequence delimiter** field will be inserted between
  the elements composing each *n*-gram in the column headers, which can
  enhance their readability. The default is ``#`` but you can change it by
  inserting the delimiter of your choice.

See also
--------

* :doc:`Getting started: Counting segment types <counting_segment_types>`
* :ref:`Reference: Count widget <Count>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :doc:`Cookbook: Segment text in smaller units <segment_text>`
* :ref:`Cookbook: Table output <cookbook_toc_table_output_ref>`

