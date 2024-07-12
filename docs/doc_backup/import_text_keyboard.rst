.. meta::
   :description: Orange Textable documentation, cookbook, import text from
                 keyboard
   :keywords: Orange, Textable, documentation, cookbook, import, text,
              keyboard

Import text from keyboard
=========================

Goal
----

Input text using keyboard for further processing with Orange Textable.

Ingredients
-----------

  ==============  =======
   **Widget**      :ref:`Text Field`
   **Icon**        |text_field_icon|
   **Quantity**    1
  ==============  =======

.. |text_field_icon| image:: figures/TextField_36.png


Procedure
---------

.. _import_text_keyboard_fig1:

.. figure:: figures/text_field_example.png
    :align: center
    :alt: Example usage of widget Text Field

    Figure 1: Importing a string using widget :ref:`Text Field`.

1. Create an instance of :ref:`Text Field` on the canvas.
2. Open its interface by double-clicking on the created instance.
3. Type text in the text field at the top of the interface.
4. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
5. A segmentation covering the input text is then available on the :ref:`Text
   Field` instance's output connections; to display or export it,
   see :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.
   
See also
--------

* :doc:`Getting started: Keyboard input and segmentation display
  <keyboard_input_segmentation_display>`
* :ref:`Reference: Text Field widget <Text Field>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

