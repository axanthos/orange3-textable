.. meta::
   :description: Orange Textable documentation, filtering segmentations using regexes
   :keywords: Orange, Textable, documentation, filter, segmentation, regex

Filtering segmentations using regexes
=====================================

In section :doc:`Using a segmentation to filter another <using_segmentation_filter_another>`,
we have seen how to use the :doc:`Intersect <intersect>`
widget to exclude a specified list of words (so-called “stopwords”) from
a segmentation. The :doc:`Select <select>`
widget is tailored for such tasks.

The widget’s interface (see :ref:`figure 1 <partitioning_segmentations_fig1>`
below) offers a choice between two modes: *Include* and *Exclude*.
Depending on this parameter, incoming segments that satisfy a given
condition will be either included in or excluded from the output
segmentation. By default (i.e. when the **Advanced settings** box is
unchecked), the condition is specified by means of a regex, which will
be applied to each incoming segment successively. For now, the option
**Annotation key** can be left to its default setting **(none)**.

.. _partitioning_segmentations_fig1:

.. figure:: figures/select_annotation_example.png
    :align: center
    :alt: Example usage of widget Select

    Figure 1: Excluding short words with widget :doc:`Select <select>`.

In the example of :ref:`figure 1 <partitioning_segmentations_fig1>`,
the widget is configured to exclude all incoming segments containing no
more than 3 letters. Note that without the *beginning of segment* and
*end of segment* anchors (``^`` and ``$``), all words containing *at least* a
sequence of 1 to 3 letters–i.e. all the words–would be excluded.

Note that
:doc:`Select <select>`
automatically emits a second segmentation containing all the segments
that have been discarded from the main output segmentation (in the case
of :ref:`figure 1 <partitioning_segmentations_fig1>`
above, that would be all words less than 4 letters long). This feature
is useful when both the selected *and* the discarded segments are to be
further processed on distinct branches. By default, when
:doc:`Select <select>`
is connected to another widget, the main segmentation is being emitted.
In order to send the segmentation of discarded segments instead,
right-click on the outgoing connection and select **Reset Signals** (see
:ref:`figure 2 <partitioning_segmentations_fig2>`
below).

.. _partitioning_segmentations_fig2:

.. figure:: figures/select_example_schema.png
    :align: center
    :alt: Right-clicking on a connection and requesting to "Reset Signals"
    :scale: 80 %

    Figure 2: Right-clicking on a connection and requesting to **Reset Signals**.

This opens the dialog shown on :ref:`figure 3 <partitioning_segmentations_fig3>`
below, where the user can “drag-and-drop” from the gray box next to
**Discarded data** up to the box next to **Segmentation**, thus
replacing the existing connection. Clicking **OK** validates the
modification and enables the discarded data to flow through the
connection.

.. _partitioning_segmentations_fig3:

.. figure:: figures/select_example_reset_signals_dialog.png
    :align: center
    :alt: Dialog for modifying the connection between two widgets
    :scale: 80 %

    Figure 3: This dialog allows the user to select a non-default connection
    between two widgets.

See also
-----------------

- :doc:`Textable's Basics: Using a segmentation to filter another <using_segmentation_filter_another>`
- :doc:`Reference: Select widget <select>`
- :doc:`Cookbook: Include/exclude segments based on a pattern <include_exclude_based_on_pattern>`
