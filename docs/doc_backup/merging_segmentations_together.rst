.. meta::
   :description: Orange Textable documentation, merging segmentations together
   :keywords: Orange, Textable, documentation, merge, data, corpus

Merging segmentations together
==============================

Computerized text analysis often implies consolidating various text sources
into a single *corpus*. In the framework of Orange Textable, this amounts
to grouping segmentations together, and it is the purpose of the
:ref:`Merge` widget.

To try out this widget, create on the canvas two instances of
:ref:`Text Field`, an instance of :ref:`Merge` and an
instance of :ref:`Display` (see
:ref:`figure 1 <merging_segmentations_together_fig1>` below). Type
a different string in each :ref:`Text Field` instance (e.g.
*a simple example* and *another example*) and assign it a distinct label (e.g.
*text_string* and *text_string2*). Eventually, connect the instances as
shown on :ref:`figure 1 <merging_segmentations_together_fig1>`.

.. _merging_segmentations_together_fig1:

.. figure:: figures/merge_example_schema.png
    :align: center
    :alt: Schema illustrating the usage of widget Merge
    :scale: 75 %

    Figure 1: Grouping *a simple example* with *another example* using widget :ref:`Merge`.

The interface of widget :ref:`Merge` (see
:ref:`figure 2 <merging_segmentations_together_fig2>` below) illustrates a
feature shared by most Orange Textable widgets: the **Advanced settings**
checkbox triggers the display of more complex controls offering more
possibilities to the user. For now we will stick to the basic settings and
leave the box unchecked.

.. _merging_segmentations_together_fig2:

.. figure:: figures/merge_example.png
    :align: center
    :alt: Interface of widget merge

    Figure 2: Interface of widget :ref:`Merge`.
    
Section **Ordering** of the widget's interface lets the user view the labels
of incoming segmentations and control the order in which they will appear in
the output segmentation (by selecting them and clicking on **Move Up** /
**Down**). The **Output segmentation label** can be set in section
**Options**. We will return :doc:`later <annotating_merging>` to the purpose
of checkbox **Import labels with key**; leave it unchecked for now.

.. _merging_segmentations_together_fig3:

.. figure:: figures/display_merged_example.png
    :align: center
    :alt: Displaying a merged segmentation

    Figure 3: Merged segmentation.

:ref:`Figure 3 <merging_segmentations_together_fig3>` above shows the
resulting merged segmentation, as displayed by widget
:ref:`Display`. As can be seen, :ref:`Merge` makes it easy
to concatenate several strings into a single segmentation. If the incoming
segmentations contained several segments, each of them would appear in the
output segmentation, in the order specified under **Ordering** (and, within
each incoming segmentation, in the original order of segments).

.. _merging_segmentations_together_ex:

**Exercise:** Can you add a new instance of :ref:`Merge` to the
schema illustrated on :ref:`figure 1 <merging_segmentations_together_fig1>`
above and modify the connections (but not the configuration of existing
widgets) so that the segmentation given in
:ref:`figure 4 <merging_segmentations_together_fig4>` below appears in the
:ref:`Display` widget?
(:ref:`solution <solution_merging_segmentations_together_ex>`)

.. _merging_segmentations_together_fig4:

.. figure:: figures/goal_exercise_merge.png
    :align: center
    :alt: 3 segments: "a simple example", "another example", "another example"

    Figure 4: The segmentation requested in the :ref:`exercise <merging_segmentations_together_ex>`.

.. _solution_merging_segmentations_together_ex:

**Solution:** (:ref:`back to the exercise <merging_segmentations_together_ex>`)

.. figure:: figures/solution_exercise_merge.png
    :align: center
    :alt: New Merge widget takes input from old one and Text field, and sends output to Display
    :scale: 70 %

    Figure 5: Solution to the :ref:`exercise <merging_segmentations_together_ex>`.

See also
--------

* :ref:`Reference: Merge widget <Merge>`
* :doc:`Cookbook: Merge several texts <merge_several_texts>`
