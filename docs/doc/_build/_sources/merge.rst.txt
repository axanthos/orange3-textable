.. meta::
   :description: Orange Textable documentation, Merge widget
   :keywords: Orange, Textable, documentation, Merge, widget

.. _Merge:

Merge
=====

.. image:: figures/Merge_54.png

Merge two or more segmentations.

Signals
-------

Inputs:

* ``Segmentation`` (multiple)

  Any number of segmentations that should be merged together

Outputs:

* ``Merged data``

  Merged segmentation

Description
-----------

This widget takes several input segmentations, successively copies each
segment of each input segmentation to form a new segmentation, and sends this
segmentation to its output connections.

.. _merge_fig1:

.. figure:: figures/merge_advanced_example.png
    :align: center
    :alt: Merge widget (advanced interface)

    Figure 1: **Merge** widget (advanced interface).

The **Options** section allows the user to import and label segments. The **Import labels with
key** checkbox enables the user to create for each input segmentation an
annotation whose value is the segmentation label (as displayed in the list)
and whose key is specified by the user in the text field on the right of the
checkbox. Similarly, the **Auto-number with key** checkbox enables the program
to automatically number the output segments and to associate the number to the
annotation key specified in the text field on the right. The **Copy
annotations** checkbox copies every input segmentation annotation to the
output segmentation.

[#]_ The **Fuse duplicate segments** checkbox enables the program to
fuse into a single segment several distinct segments whose addresses are the
same; the annotations associated to the fused segments are all copied in the
single resulting segment. [#]_

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface or when its input data are
modified (by deletion or addition of a connection, or because modified data is
received through an existing connection).

Below the **Send** button, the user finds the number of segments in the output
segmentation, or the reasons why no segmentation is emitted (no input data,
no label specified for the output segmentation, etc.).

Messages
--------

Information
~~~~~~~~~~~

*Data correctly sent to output: <n> segments.*
    This confirms that the widget has operated properly.

*Settings were* (or *Input has*) *changed, please click 'Send' when ready.*
    Settings and/or input have changed but the **Send automatically** checkbox
    has not been selected, so the user is prompted to click the **Send**
    button (or equivalently check the box) in order for computation and data
    emission to proceed.

*No data sent to output yet: no input segmentation.*
    The widget instance is not able to emit data to output because it receives
    none on its input channel(s).

*No data sent to output yet, see 'Widget state' below.*
    A problem with the instance's parameters and/or input data prevents it
    from operating properly, and additional diagnostic information can be
    found in the **Widget state** box at the bottom of the instance's
    interface (see `Warnings`_ below).

Warnings
~~~~~~~~

*No label was provided.*
    A label must be entered in the **Output segmentation label** field in
    order for computation and data emission to proceed.
    
*No annotation key was provided for imported labels.*
    The **Import labels with key** checkbox has been selected and an annotation
    key must be specified in the text field on the right in order for
    computation and data emission to proceed.
    
*No annotation key was provided for auto-numbering.*
    The **Auto-number with key** checkbox has been selected and an annotation
    key must be specified in the text field on the right in order for
    computation and data emission to proceed.
    
Examples
--------

* :doc:`Getting started: Merging segmentations together
  <merging_segmentations_together>`
* :doc:`Getting started: Annotating by merging <annotating_merging>`
* :doc:`Cookbook: Merge several texts <merge_several_texts>`

See also
--------

* :doc:`Getting started: Tagging table rows with annotations
  <tagging_table_rows_annotations>`

Footnotes
---------

.. [#] Note that if sorting is enabled, it may well result in segments being
       ordered in a different way than specified by the user in the
       **Ordering** section.

.. [#] In the case where the fused segments have distinct values for the same
       annotation key, only the value of the last segment (in the order of the
       output segmentation before fusion) will be retained.


