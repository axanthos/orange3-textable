.. meta::
   :description: Orange Textable documentation, examine evolution of unit 
                 frequency along the text
   :keywords: Orange, Textable, documentation, cookbook, evolution, unit, 
              frequency, sliding window

Examine the evolution of unit frequency along the text
======================================================

Goal
----

Examine how the frequency of segment types evolves from the beginning to the
end of a segmentation.

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

.. _examine_evolution_unit_frequency_along_text_fig1:

.. figure:: figures/count_unit_frequency_gradually.png
   :align: center
   :alt: Examine the evolution of unit frequency with an instance of Count

   Figure 1: Examine the evolution of unit frequency with an instance of 
   :ref:`Count`

1. Create an instance of :ref:`count` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that has been used to segment the text (e.g. :ref:`Segment`) to
   the :ref:`Count` widget instance's input connection (lefthand side).
3. Open the :ref:`Count` instance's interface by double-clicking on its
   icon on the canvas.
4. In the **Units** section, select the segmentation whose units will be
   counted.
5. In the **Context** section, choose **Mode: Sliding window**.
6. Set the **Window size** parameter to the desired value; with the minimum
   value of 1, frequency will be counted separately at every successive
   position in the segmentation, whereas a larger value *n* > 1 will have the
   effect that frequency will be counted in larger and partially overlapping
   spans (segments 1 to *n*, then 2 to *n* + 1, and so on), resulting in a
   smoother curve.
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

See also
--------

* :ref:`Reference: Count widget <Count>`
* :doc:`Cookbook: Segment text <segment_text>`
* :doc:`Cookbook: Display table <display_table>`

