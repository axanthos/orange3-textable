Filter segments based on their frequency
============================================

Goal
--------

Filter out the most rare and/or frequent segments of a segmentation.

Prerequisites
-----------------

Some text has been imported in Orange Textable (see :doc:`Cookbook: Text input <text_input>`) and in all likelihood it has been segmented in smaller units (see :doc:`Cookbook: Segment text in smaller units <segment_text>`).

Ingredients
---------------

  ==============  ============== 
   **Widget**      :doc:`Select <select>` 
   **Icon**        |select_icon|  
   **Quantity**    1               
  ==============  ==============

.. |select_icon| image:: figures/Select_36.png

Procedure
-------------

.. _filter_segments_based_on_frequency_fig1:

.. figure:: figures/filter_segments_based_on_frequency.png
   :align: center
   :alt: Filtering out low-frequency segments with an instance of Select

   Figure 1: Filtering out low-frequency segments with an instance of :doc:`Select <select>`


1. Create an instance of :doc:`Select <select>`.

2. Drag and drop from the output (righthand side) of the widget that emits the segmentation to be filtered, here :doc:`Segment <segment>` (*letters*), to the input of :doc:`Select <select>` (lefthand side).

3. Double-click on the icon of :doc:`Select <select>` to open its interface.

4. Tick the **Advanced settings** checkbox.

5. In the **Select** section, choose **Threshold** in the **Method** drop-down menu.

6. Under **Threshold expressed as**, choose whether you want to express frequency thresholds in terms of **Count** (i.e. number of tokens) or of **Proportion** (i.e. percentage of tokens).

7. If you want to set a minimum frequency threshold, tick the **Min. count** (respectively **Min. proportion (%)**) checkbox and indicate the minimum frequency that a segment type must have in order to be included in the output.

8. If you want to set a maximum frequency threshold, tick the **Max. count** (respectively **Max. proportion (%)**) checkbox and indicate the maximum frequency that a segment type can have in order to be included in the output.

9. Click the **Send** button or tick the **Send automatically** checkbox.

10. A segmentation containing the selected segments is then available at the output of :doc:`Select <select>`; to display or export it, see :doc:`Cookbook: Text output <text_output>`.

Comment
-----------

- The :doc:`Select <select>` widget emits on a second output connection (not selected by default) a segmentation containing the segments that were *not* selected (see :doc:`Filtering segmentations using regexes <filtering_segmentations_regexes>` for instructions on how to access this other output segmentation).

See also
------------

- :doc:`Reference: Select widget <select>`
- :doc:`Cookbook: Text input <text_input>`
- :doc:`Cookbook: Segment text in smaller units <segment_text>`
- :doc:`Cookbook: Text output <text_output>`
