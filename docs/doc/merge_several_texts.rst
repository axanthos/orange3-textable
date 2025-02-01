Merge several texts
=======================

Goal
--------

Merge several texts together so they can be further processed as a whole.

Prerequisites
-----------------

Two or more texts have been imported in Orange Textable (see :doc:`Cookbook: Text input <text_input>`) 
and possibly further processed (see :doc:`Cookbook: Segmentation manipulation <segmentation_manipulation>`).

Ingredients
---------------


  ==============  ==================  
   **Widget**      :doc:`Merge <merge>`   
   **Icon**        |merge_icon|    
   **Quantity**    1                 
  ==============  ==================  
  
.. |merge_icon| image:: figures/Merge_36.png

Procedure
-------------

.. _merge_several_texts_fig1:

.. figure:: figures/merge_several_texts.png
   :align: center
   :alt: Merge several texts with an instance of Merge
   :scale: 75%

   Figure 1: Merge several texts with an instance of :doc:`Merge <merge>`

1. Create an instance of :doc:`Merge <merge>`.

2. Drag and drop from the output (righthand side) of the widgets that emit the segmentations to be merged together, here :doc:`Text Files <text_files>` (*Hamlet*) and :doc:`Text Files <text_files>` (*Macbeth*), to the input of :doc:`Merge <merge>` (lefthand side).

3. Double-click on the icon of :doc:`Merge <merge>` to open its interface.

4. Click the **Send** button or tick the **Send automatically** checkbox.

5. A segmentation containing all input data merged together is then available at the output of :doc:`Merge <merge>`; to display or export it, see :doc:`Cookbook: Text output <text_output>`.


See also
------------

- :doc:`Textable's Basics: Merging segmentations together <merging_segmentations_together>`
- :doc:`Reference: Merge widget <merge>`
- :doc:`Cookbook: Text input <text_input>`
- :doc:`Cookbook: Segmentation manipulation <segmentation_manipulation>`
- :doc:`Cookbook: Text output <text_output>`