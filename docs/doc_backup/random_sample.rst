.. meta::
   :description: Orange Textable documentation, create a random selection or 
                 sample of segments
   :keywords: Orange, Textable, documentation, cookbook, random, selection,
              sample, segments
   
Create a random selection or sample of segments
===============================================

Goal
----

Create a random sample of segments.

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

.. _create_random_selection_sample_of_segments_fig1:

.. figure:: figures/random_sample_Sample_mode.png
   :align: center
   :alt: Create a random selection or sample of segments with an instance of 
         Select

   Figure 1: Create a random selection or sample of segments with an instance
   of :ref:`Select`

1. Create an instance of :ref:`Select` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation to be sampled (e.g. an instance of
   :ref:`Segment`) to the :ref:`Select` instance's input connection (lefthand
   side).
3. Open the :ref:`Select` instance's interface by double-clicking on its
   icon on the canvas.
4. Tick the **Advanced settings** checkbox.
5. In the **Select** section, choose the **Method:** **Sample**.
6. Under **Sample size expressed as**, choose whether you want to express
   sample size in terms of **Count** (i.e. number of tokens) or of
   **Proportion** (i.e. percentage of tokens).
7. In the **Sample size** control, choose the number of segments that will be
   randomly sampled (respectively, choose the percentage of segments in the
   **Sampling rate (%)** control).
8. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
9. A segmentation containing the sampled segments is then available on the
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

