.. meta::
   :description: Orange Textable documentation, cookbook, merge several texts
   :keywords: Orange, Textable, documentation, cookbook, merge, texts

Merge several texts
===================

Goal
----

Merge several texts together so they can be further processed as a whole.

Prerequisites
-------------

Two or more text have been imported in Orange Textable (see :ref:`Cookbook:
Text input <cookbook_toc_text_input_ref>`) and possibly further processed (see
:ref:`Cookbook: Segmentation manipulation
<cookbook_toc_segmentation_manipulation_ref>`).

Ingredients
-----------

  ==============  ==================  
   **Widget**      :ref:`Merge`   
   **Icon**        |merge_icon|    
   **Quantity**    1                 
  ==============  ==================  
  
.. |merge_icon| image:: figures/Merge_36.png


Procedure
---------

.. _merge_several_texts_fig1:

.. figure:: figures/merge_several_texts.png
   :align: center
   :alt: Merge several texts with an instance of Merge

   Figure 1: Merge several texts with an instance of :ref:`Merge`
   
1. Create an instance of :ref:`Merge` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instances that emit the segmentations to be merged together (e.g. two
   instances of :ref:`Text Field`) to the :ref:`Merge` instance's input
   connection (lefthand side).
3. Open the :ref:`Merge` widget instance's interface by double-clicking on its 
   icon on the canvas.
4. All input data appear in the **Ordering** section; you can change their
   ordering by selecting a line and clicking on **Move Up** or **Move
   Down**.
5. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
6. A segmentation containing all input data merged together is then available
   on the :ref:`Merge` instance's output connections; to display or export
   it, see :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.

See also
--------

* :doc:`Getting started: Merging segmentations together
  <merging_segmentations_together>`
* :ref:`Reference: Merge widget <Merge>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :ref:`Cookbook: Segmentation manipulation
  <cookbook_toc_segmentation_manipulation_ref>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

