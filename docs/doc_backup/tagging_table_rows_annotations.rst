.. meta::
   :description: Orange Textable documentation, tagging table rows with
                 annotations
   :keywords: Orange, Textable, documentation, table, row, annotations

Tagging table rows with annotations
===================================

There are several situations in which annotations attached to a segment can be
used in place of this segment's content. A particularly common case consists
in using annotations for tagging the rows of a table built with an instance
of :ref:`Count`, :ref:`Length`, :ref:`Variety`, or :ref:`Category`.

Consider the example of the texts in English and French introduced
:doc:`here <annotating_merging>`. Suppose that after having merged them into
a single segmentation with an instance of :ref:`Merge` (**Output segmentation
label:** *texts*), we segment these three texts into letters with an instance
of :ref:`Segment` (**Regex** ``\w``, **Output segmentation label:** *letters*),
as in the schema shown on
:ref:`figure 1 <tagging_table_rows_annotations_fig1>` below; both
segmentations (*texts* and *letters*) can then be sent to an instance of
:ref:`Count` for building a table with the frequency of each letter in
each text.

.. _tagging_table_rows_annotations_fig1:

.. figure:: figures/tagging_rows_annotations_schema.png
    :align: center
    :alt: Counting letter frequency in three texts
    :scale: 80%
    
    Figure 1: Schema for counting letter frequency in three texts.

Let us suppose, first, that the instance of :ref:`Count` is configured as
shown on :ref:`figure 2 <tagging_table_rows_annotations_fig2>` below, so that
the definition of contexts--that is, rows of the frequency table--is based on
the content of the three texts.

.. _tagging_table_rows_annotations_fig2:

.. figure:: figures/count_tagging_rows_annotations.png
    :align: center
    :alt: Counting letter frequency in three texts

    Figure 2: Counting letter frequency in texts.

Here is the resulting table, disregarding possible variations in row and/or
column order:

.. _tagging_table_rows_annotations_table1:

.. csv-table:: Table 1: Letter frequency in three texts.
    :header: "", *a*, *t*, *e*, *x*, *i*, *n*, *E*, *g*, *l*, *s*, *h*, *o*, *r*, *u*, *f*, *ç*
    :stub-columns: 1
    :widths: 7 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2

    *a text in English*,       1, 2, 1, 1, 2, 2, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0
    *another text in English*, 1, 3, 2, 1, 2, 3, 1, 1, 1, 1, 2, 1, 1, 0, 0, 0
    *un texte en français*,    2, 2, 3, 1, 1, 3, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1

As can be seen, the default header of each row is the entire content of each 
text. While this may not be a problem in a pedagogic example like this one,
it is easy to see why it would compromise the table's readability in a real 
application, where texts often contain thousand or even millions of 
characters. To avoid that, it is useful to tag the table's rows with 
annotation values attached to segments rather than with these segments'
content. To that effect, the desired annotation key must be selected in the
**Contexts** section of widget :ref:`Count`'s interface.
 
.. _tagging_table_rows_annotations_fig3:

.. figure:: figures/count_tagging_rows_annotations_language.png
    :align: center
    :alt: Tagging contexts with annotation values

    Figure 3: Tagging contexts with annotation values.

In the example of :ref:`figure 3 <tagging_table_rows_annotations_fig3>` above
key *language* has been selected, so that the resulting frequency table looks
like this:

.. _tagging_table_rows_annotations_table2:

.. csv-table:: Table 2: Letter frequency in two text types.
    :header: "", *a*, *t*, *e*, *x*, *i*, *n*, *E*, *g*, *l*, *s*, *h*, *o*, *r*, *u*, *f*, *ç*
    :stub-columns: 1
    :widths: 3 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2

    *en*, 2, 5, 3, 2, 4, 5, 2, 2, 2, 2, 3, 1, 1, 0, 0, 0
    *fr*, 2, 2, 3, 1, 1, 3, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1

Besides the substitution of segment content by annotation values in row 
headers, this example demonstrates an important consequence of this 
manipulation: contexts associated with the same annotation value are, in 
effect, collapsed together so that they form a single row. If this behavior
is not desired, it can be avoided by assigning distinct annotation values to
the contexts that must be kept separated (e.g. *en_1* and *en_2*).

See also
--------

* :doc:`Getting started: Annotating by merging <annotating_merging>`
* :ref:`Reference: Merge widget <Merge>`
* :ref:`Reference: Segment widget <Segment>`
* :ref:`Reference: Count widget <Count>`
* :ref:`Reference: Table construction widgets <table_construction_widgets>`


