.. meta::
   :description: Orange Textable documentation, from segmentation to tables
   :keywords: Orange, Textable, documentation, segmentations, tables

From segmentations to tables
============================

The main purpose of Orange Textable is to build tables based on texts.
Central to this process are the segmentations we have learned to create
and manipulate earlier. Indeed, Orange Textable provides a number of
:doc:`widgets for table construction <table_construction_widgets>`,
and they all operate on the basis of one or more segmentations.

For the time being, we will focus on the construction of frequency
tables, which are very common in computerized text analysis and which
will serve as an introduction to other types of tables. For the sake of
simplicity, consider first the segmentation of *a simple example* into
letters. Counting the frequency of each letter type yields a table such
as the following:

.. _segmentations_tables_table1:

+-------+---+
| **a** | 2 |
+-------+---+
| **s** | 1 |
+-------+---+
| **i** | 1 |
+-------+---+
| **m** | 2 |
+-------+---+
| **p** | 2 |
+-------+---+
| **l** | 2 |
+-------+---+
| **e** | 3 |
+-------+---+
| **x** | 2 |
+-------+---+

More often, we will be interested in comparing frequency across several
*contexts*. For instance, if the word segmentation of *a simple example*
is also available, it may be used together with the letter segmentation
to produce a so-called *contingency table* (or *document–term matrix*):

.. _segmentations_tables_table2:

+-------------+-------+-------+-------+-------+-------+-------+-------+-------+
|             | **a** | **s** | **i** | **m** | **p** | **l** | **e** | **x** |
+=============+=======+=======+=======+=======+=======+=======+=======+=======+
| **a**       | 1     | 0     | 0     | 0     | 0     | 0     | 0     | 0     |
+-------------+-------+-------+-------+-------+-------+-------+-------+-------+
| **simple**  | 0     | 1     | 1     | 1     | 1     | 1     | 1     | 0     |
+-------------+-------+-------+-------+-------+-------+-------+-------+-------+
| **example** | 1     | 0     | 0     | 1     | 1     | 1     | 2     | 1     |
+-------------+-------+-------+-------+-------+-------+-------+-------+-------+


In a real application, rows could correspond to the writings of an
author and columns to selected prepositions, for instance. The general
idea is to determine the number of occurrences of various *units* in
various *contexts*. Such data can then be further analyzed, typically by
means of a statistical test (aiming at answering the question “does the
distribution of units depend on contexts”) or a graphical representation
(making it possible to visualize the attraction or repulsion between
specific units and contexts).

See also
-----------------

- :doc:`Reference: Table construction widgets <table_construction_widgets>`