.. meta::
   :description: Orange Textable documentation, include or exclude segments
                 based on a pattern
   :keywords: Orange, Textable, documentation, cookbook, include, exclude, 
              segments, pattern

Include/exclude segments based on a pattern
===========================================

Goal
----

Include or exclude segments from a segmentation using a regular expression

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and in all likelihood it has been segmented
in smaller units (see :doc:`Cookbook: Segment text in smaller units
<segment_text>`).

Ingredients
-----------

  ==============  ================  
   **Widget**      :ref:`Select`   
   **Icon**        |select_icon|    
   **Quantity**    1                
  ==============  ================ 

.. |select_icon| image:: figures/Select_36.png

Procedure
---------

.. _include_exclude_units_based_on_pattern_fig1:

.. figure:: figures/include_exclude_units_based_on_pattern.png
   :align: center
   :alt: Include or exclude units based on a pattern with an instance of Select

   Figure 1: Using the :ref:`Select` widget to include/exclude segments
   from a segmentation based on a regular expression
   
 
1. Create an instance of :ref:`Select` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation to be filtered (e.g. an instance of
   :ref:`Segment`) to the :ref:`Select` instance's input connection (lefthand
   side).
3. Open the :ref:`Select` instance's interface by double-clicking on its
   icon on the canvas.
4. In the **Select** section, choose either **Mode:** **Include** or
   **Exclude**.
5. In the **Regex** field, insert the pattern that will select the units to
   be included or excluded, such as the single letter ``e`` in our example.
6. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
7. A segmentation containing the selected segments is then available on the
   :ref:`Select` instance's output connections; to display or export it, see
   :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.

Comment
-------

* In the **Regex** field you can use all the syntax of Python's regular
  expression (*cf.* `Python documentation
  <http://docs.python.org/library/re.html>`_).
* The :ref:`Select` widget emits on a second output connection (not selected
  by default) a segmentation containing the segments that were *not* selected.

See also
--------

* :doc:`Getting started: Partitioning segmentations
  <partitioning_segmentations>`
* :ref:`Reference: Select widget <Select>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :doc:`Cookbook: Segment text in smaller units <segment_text>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

