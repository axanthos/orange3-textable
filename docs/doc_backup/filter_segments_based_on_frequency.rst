.. meta::
   :description: Orange Textable documentation, cookbook, filter segments
                 based on their frequency

   :keywords: Orange, Textable, documentation, cookbook, filter, segments,
              frequency

Filter segments based on their frequency
========================================

Goal
----

Filter out the most rare and/or frequent segments of a segmentation.

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and in all likelihood it has been segmented
in smaller units (see :doc:`Cookbook: Segment text in smaller units
<segment_text>`).

Ingredients
-----------

  ==============  ============== 
   **Widget**      :ref:`Select` 
   **Icon**        |select_icon|  
   **Quantity**    1               
  ==============  ==============

.. |select_icon| image:: figures/Select_36.png

Procedure
---------

.. _filter_segments_based_on_frequency_fig1:

.. figure:: figures/filter_segments_based_on_frequency.png
   :align: center
   :alt: Filtering out low-frequency segments with an instance of Select

   Figure 1: Filtering out low-frequency segments with an instance of
   :ref:`Select`

1. Create an instance of :ref:`Select` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation to be filtered (e.g. an instance of
   :ref:`Segment`) to the :ref:`Select` instance's input connection (lefthand
   side).
3. Open the :ref:`Select` instance's interface by double-clicking on its
   icon on the canvas.
4. Tick the **Advanced settings** checkbox.
5. In the **Select** section, choose **Threshold** in the **Method** drop-down 
   menu.
6. Under **Threshold expressed as**, choose whether you want to express
   frequency thresholds in terms of **Count** (i.e. number of tokens) or of
   **Proportion** (i.e. percentage of tokens).
7. If you want to set a minimum frequency threshold, tick the **Min. count**
   (respectively **Min. proportion (%)**) checkbox and indicate the minimum
   frequency that a segment type must have in order to be included in the
   output.
8. If you want to set a maximum frequency threshold, tick the **Max. count**
   (respectively **Max. proportion (%)**) checkbox and indicate the maximum
   frequency that a segment type can have in order to be included in the
   output.
9. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
10. A segmentation containing the selected segments is then available on the
    :ref:`Select` instance's output connections; to display or export it, see
    :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.

Comment
-------

* The :ref:`Select` widget emits on a second output connection (not selected
  by default) a segmentation containing the segments that were *not* selected.

See also
--------

* :ref:`Reference: Select widget <Select>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :doc:`Cookbook: Segment text in smaller units <segment_text>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

