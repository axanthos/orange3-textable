.. meta::
   :description: Orange Textable documentation, cookbook, display text content
   :keywords: Orange, Textable, documentation, cookbook, display, text,
              content

Display text content
====================

Goal
----

Display the content of a text (segmentation).

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and possibly further processed (see
:ref:`Cookbook: Segmentation manipulation
<cookbook_toc_segmentation_manipulation_ref>`).

Ingredients
-----------

  ==============  =======
   **Widget**      :ref:`Display`
   **Icon**        |display_icon|
   **Quantity**    1
  ==============  =======

.. |display_icon| image:: figures/Display_36.png

Procedure
---------

.. _display_text_content_fig1:

.. figure:: figures/display_example.png
   :align: center
   :alt: Viewing text with an instance of Display

   Figure 1: Viewing text with an instance of :ref:`Display`.

1. Create an instance of :ref:`Display` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation to be displayed (e.g.
   :ref:`Text Field`) to the :ref:`Display` instance's input connection
   (lefthand side).
3. Open the :ref:`Display` instance's interface by double-clicking on its
   icon on the canvas to view the text content.
   
Comment
-------

* If the input data consist of a large number of segments (thousands or more),
  the time necessary to display them can be prohibitively long.

See also
--------

* :doc:`Getting started: Keyboard input and segmentation display
  <keyboard_input_segmentation_display>`
* :ref:`Reference: Display widget <Display>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :ref:`Cookbook: Segmentation manipulation
  <cookbook_toc_segmentation_manipulation_ref>`

