.. meta::
   :description: Orange Textable documentation, cookbook, segment text in
                 smaller units
   :keywords: Orange, Textable, documentation, cookbook, segment, text, units,
              lines, words, letters

Segment text in smaller units
=============================

Goal
----

Segment text in smaller units (e.g. lines, words, letters, etc.).

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and possibly further processed (see
:ref:`Cookbook: Segmentation manipulation
<cookbook_toc_segmentation_manipulation_ref>`).

Ingredients
-----------

  ==============  =======
   **Widget**      :ref:`Segment`
   **Icon**        |segment_icon|
   **Quantity**    1
  ==============  =======

.. |segment_icon| image:: figures/Segment_36.png

Procedure
---------

.. _segment_text_fig1:

.. figure:: figures/segment_text.png
   :align: center
   :alt: Segment text in lines with an instance of Segment

   Figure 1: Segment text in lines with an instance of :ref:`Segment`.
   
1. Create an instance of :ref:`Segment` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation to be segmented (e.g.
   :ref:`Text Field`) to the :ref:`Segment` instance's input connection
   (lefthand side).
3. Open the :ref:`Segment` instance's interface by double-clicking on its
   icon on the canvas.
4. In the **Regex** section, insert the regular expression describing the
   units that will be segmented (for example to segment a text in lines use
   ``.+``, in words ``\w+``, in letters ``\w``, in characters ``.``, and so
   on) then click on the validation button on the right.
5. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
6. A segmentation containing a segment for each specified unit (e.g. line) is
   then available on the :ref:`Segment` instance's output connections; to
   display or export it, see :ref:`Cookbook: Text output
   <cookbook_toc_text_output_ref>`.

Comment
-------
* In the **Regex** field you can use all the syntax of Python's regular
  expression (*cf.* `Python documentation
  <http://docs.python.org/library/re.html>`_).

See also
--------

* :doc:`Getting started: Segmenting data into smaller units
  <segmenting_data_smaller_units>`
* :ref:`Reference: Segment widget <Segment>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :ref:`Cookbook: Segmentation manipulation
  <cookbook_toc_segmentation_manipulation_ref>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

