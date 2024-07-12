.. meta::
   :description: Orange Textable documentation, count occurrences of smaller 
                 units in larger segments
   :keywords: Orange, Textable, documentation, cookbook, count, occurrences, 
              units, contexts, term-document matrix, document-term matrix,
              contingency table

Count occurrences of smaller units in larger segments
=====================================================

Goal
----

Count the occurrences of smaller units (for instance letters) in larger
segments (for instance words), and report the results by means of a
two-dimensional contingency table (e.g. with words in rows and letters in
columns).

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and it has been segmented in at least two
hierarchical levels, e.g. words and letters (see :doc:`Cookbook: Segment text
in smaller units <segment_text>`).

Ingredients
-----------

  ==============  =============
   **Widget**      :ref:`Count`   
   **Icon**        |count_icon|  
   **Quantity**    1          
  ==============  =============

.. |count_icon| image:: figures/Count_36.png

Procedure
---------

.. _count_occurrences_smaller_units_in_larger_segments_fig1:

.. figure:: figures/count_occurrences_other_smaller_segmentation.png
   :align: center
   :alt: Count occurrences of a smaller units in larger segments with an 
         instance of Count

   Figure 1: Count occurrences of smaller units in larger segments with an 
   instance of :ref:`Count`

1. Create an instance of :ref:`Count` on the canvas.
2. Drag and drop from the output connection (righthand side) of both widget
   instances that have been used to segment the text
   (here the two instances of :ref:`Segment`) to the :ref:`Count` widget
   instance's input connection (lefthand side), thus forming a triangle.
3. Open the :ref:`Count` instance's interface by double-clicking on its
   icon on the canvas.
4. In the **Units** section, select the segmentation into smaller units (here:
   *letters*).
5. In the **Context** section, choose **Mode: Containing segmentation**.
6. In the **Segmentation** field, select the context segmentation, i.e. the
   segmentation into larger segments (here *words*).
7. Click the **Compute** button (or make sure the **Compute automatically**
   checkbox is selected).
8. A table showing the results is then available at the output connection of
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

* :doc:`Getting started: Counting in specific contexts
  <counting_specific_contexts>`
* :ref:`Reference: Count widget <Count>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :doc:`Cookbook: Segment text in smaller units <segment_text>`
* :ref:`Cookbook: Table output <cookbook_toc_table_output_ref>`

