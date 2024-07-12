.. meta::
   :description: Orange Textable documentation, merging units with annotations
   :keywords: Orange, Textable, documentation, merge, units, annotations

Merging units with annotations
==============================

Annotations can also be used for merging *units* (that is, columns) during
counting operations in particular. Consider again the example of annotations
extracted from XML data developed
:doc:`here <converting_xml_markup_annotations>`. The segmentation produced by
:ref:`Extract XML` can be sent to an instance of :ref:`Count` as on the schema
shown on :ref:`figure 1 <merging_units_annotations_fig1>` below.

.. _merging_units_annotations_fig1:

.. figure:: figures/merging_units_annotations_schema.png
    :align: center
    :alt: Counting segments extracted from XML data
    :scale: 80%

    Figure 1: Counting segments extracted from XML data.

If the *type* annotation key is selected in section **Units** of widget
:ref:`Count`'s interface (see :ref:`figure 2 <merging_units_annotations_fig2>`
below), the annotation values correponding to this key (namely part of speech)
will be counted in place of the segments' content.

.. _merging_units_annotations_fig2:

.. figure:: figures/count_merging_units_annotations.png
    :align: center
    :alt: Counting segments extracted from XML data

    Figure 2: Merging units using annotation values.

The resulting table is as follows:

.. _merging_units_annotations_table1:

.. csv-table:: Table 1: Part of speech frequency.
    :header: *NOUN*, *DET*, *PREP*
    :stub-columns: 0

    3, 1, 1

Of course, annotations may be used to merge units *and* contexts
simultaneously.

See also
--------

* :doc:`Getting started: Converting XML markup to annotations
  <converting_xml_markup_annotations>`
* :ref:`Reference: Extract XML widget <Extract XML>`
* :ref:`Reference: Count widget <Count>`

