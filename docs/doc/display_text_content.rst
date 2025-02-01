.. meta::
   :description: Orange Textable documentation, text output
   :keywords: Orange, Textable, documentation, text, output

Display text content
====================

Goal
--------

Display the content of a text (segmentation).

Prerequisites
-----------------

Some text has been imported in Orange Textable (see :doc:`Cookbook: Text input <text_input>`)
and possibly further processed (see :doc:`Cookbook: Segmentation manipulation <segmentation_manipulation>`).

Ingredients
---------------

  ==============  =======
   **Widget**      :doc:`Display <display>`
   **Icon**        |display_icon|
   **Quantity**    1
  ==============  =======

.. |display_icon| image:: figures/Display_36.png

Procedure
-------------

.. _display_text_content_fig1:

.. figure:: figures/display_example.png
   :align: center
   :alt: Viewing text with an instance of Display
   :scale: 75%

   Figure 1: Viewing text with an instance of :doc:`Display <display>`.

1. Create an instance of
   :doc:`Display <display>`.

2. Drag and drop from the output (righthand side) of the widget that
   emits the segmentation to be displayed, here :doc:`Text Field <text_field>`
   (*Hamlet*), to the input of :doc:`Display <display>`
   (lefthand side).

3. Double-click on the icon of :doc:`Display <display>`
   to view the text content. You can show the segmentation in HTML
   format if you check the option (Figure 1)

Comment
-----------

-  If the input segmentation is large (>1000 segments), the time
   necessary to display it in HTML format can be prohibitively long. For
   this reason, only the first 5 segments and the last 5 segments are
   displayed by default in this case. If you want all segments displayed
   nevertheless, tick the **Advanced Settings** checkbox then uncheck
   **Limit number of displayed segments**.

See also
------------

- :doc:`Textable's Basics: Keyboard input and segmentation display <keyboard_input_segmentation_display>`
- :doc:`Reference: Display widget <display>`
- :doc:`Cookbook: Text input <text_input>`
- :doc:`Cookbook: Segmentation manipulation <segmentation_manipulation>`
