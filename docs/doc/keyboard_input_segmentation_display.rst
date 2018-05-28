.. meta::
   :description: Orange Textable documentation, keyboard input and
                 segmentation display
   :keywords: Orange, Textable, documentation, keyboard, input, segmentation,
              display

Keyboard input, widget labelling and segmentation display
=======================================

Typing text in a :ref:`Text Field` widget is the simplest way to
import a string in Orange Textable. As a result, the widget creates a segmentation with a single segment covering the entire string. (see
:ref:`figure 1 <keyboard_input_segmentation_fig1>` below):

.. _keyboard_input_segmentation_fig1:

.. figure:: figures/text_field_example.png
    :align: center
    :alt: Example usage of widget Text Field

    Figure 1: Typing some simple examples in widget :ref:`Text Field`.
Each segmentation is identified by a label which is the name of the widget that creates the segmentation. 
You can rename this widget to make the label more meaningful (see figure 1 below). 
As we will see later, a segmentation can also store annotations associated with segments. 
    
This widget's simplicity makes it most adequate for pedagogic purposes. Later,
we will discover other, more powerful ways of importing strings.

The :ref:`Display` widget can be used to visualize the details
of a segmentation. By default, it shows the segmentation's label followed by
each successive segment's address and content. A segmentation sent by a
:ref:`Text Field` instance will contain a single segment
covering the whole string (see :ref:`figure 2
<keyboard_input_segmentation_fig2>` below).

.. _keyboard_input_segmentation_fig2:

.. figure:: figures/display_example.png
    :align: center
    :alt: Example usage of widget Display

    Figure 2: Viewing *a simple example* in widget :ref:`Display`.
    
By default, :ref:`Display` passes its input data without
modification to its output connections. It is very useful for viewing
intermediate results in an Orange Textable schema and making sure that other
widgets process data as expected.
    
See also
--------

* :ref:`Reference: Text Field widget <Text Field>`
* :ref:`Reference: Display widget <Display>`
* :doc:`Cookbook: Import text from keyboard <import_text_keyboard>`
* :doc:`Cookbook: Display text content <display_text_content>`


