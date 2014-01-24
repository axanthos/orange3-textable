Keyboard input and segmentation display
=======================================

Typing text in a :ref:`Text Field` widget is the simplest way to
import a string in Orange Textable. This widget has no input connections, and
emits in output a segmentation containing a single segment whose address
points to the entire string that was typed. This segmentation is assigned the
label specified in the **Output segmentation label** field (see
:ref:`figure 1 <keyboard_input_segmentation_fig1>` below):

.. _keyboard_input_segmentation_fig1:

.. figure:: figures/text_field_example.png
    :align: center
    :alt: Example usage of widget Text Field
    :figclass: align-center

    Figure 1: Typing *a simple example* in widget :ref:`Text Field`.
    
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
    :figclass: align-center

    Figure 2: Viewing *a simple example* in widget :ref:`Display`.
    
By default, :ref:`Display` passes its input data without
modification to its output connections. It is very useful for viewing
intermediate results in an Orange Textable schema and making sure that other
widgets process data as expected.
    



