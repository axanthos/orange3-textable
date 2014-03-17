.. _Text Field:

Text Field
==========

.. image:: figures/TextField_54.png

Import text data from keyboard input.

Signals
-------

Inputs: none

Outputs:

* ``Text data``

  Segmentation covering the input text
  
Description
-----------

This widget allows the user to import keyboard collected data. It emits a
segmentation containing a unique unannoted segment covering the whole string.
The interface of the widget is divided in three zones (see
:ref:`figure 1 <text_field_fig1>` below). The
upper part is a text field editable by the user. The standard editing
functions (copy, paste, cancel, etc.) are accessible through a right-click on
the surface of the field.

.. _text_field_fig1:

.. figure:: figures/text_field_example.png
    :align: center
    :alt: Interface of the Text field widget
    :figclass: align-center

    Figure 1: Interface of the *Text field* widget.

The **Options** section allows the user to define the label of the output
segmentation (**Output segmentation label**), here *text_string*.

The **Info** section indicates the length of the output segmentation in
characters, or the reasons why no segmentation is emitted (in particular if no
text has been entered in the field). In the example, the single segment
contained in the output segmentation covers 16 characters.

The **Send** button triggers data emission, as it happens a segmentation, to
the output connection(s). When it is selected, the **Send automatically**
checkbox disables the button and the widget attempts to automatically emit
a segmentation at every modification of its interface (editing of the text or
label modification).

It should be noted that the text field's content is systematically converted
to Unicode; moreover, it is subjected to the `canonical Unicode
decomposition-recomposition <http://unicode.org/reports/tr15>`_  technique:
Unicode sequences such as ``LATIN SMALL LETTER C (U+0063)`` + ``COMBINING
CEDILLA (U+0327)`` are systematically replaced by the combined equivalent,
e.g. ``LATIN SMALL LETTER C WITH CEDILLA (U+00C7)``.

Examples
--------

:doc:`Keyboard input and segmentation display <keyboard_input_segmentation_display>`

See also:

* :doc:`Merging segmentations together <merging_segmentations_together>`
* :doc:`Using a segmentation to filter another <using_segmentation_filter_another>`
* :doc:`Counting segment types <counting_segment_types>`
* :doc:`Annotating by merging <annotating_merging>`
* :doc:`Converting XML markup to annotations <converting_xml_markup_annotations>`
* :doc:`Tagging table rows with annotations <tagging_table_rows_annotations>`


