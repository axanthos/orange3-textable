.. meta::
   :description: Orange Textable documentation, segmenting data into smaller
                 units
   :keywords: Orange, Textable, documentation, segment, words, letters, units

Segmenting data into smaller units
==================================

We have seen :doc:`previously <merging_segmentations_together>` how to combine
several segmentations into a single one. We will often be performing the
inverse operation: create a segmentation whose segments are *parts* of another
segmentation's segments. Typically, we will be segmenting strings into words,
characters, or any kind of text units that will be later counted, measured,
and so on. This is precisely the purpose of widget :ref:`Segment`.

To try it out, create a new schema with an instance of :ref:`Text Field`
connected to an instance of :ref:`Segment`, itself connected to an instance of
:ref:`Display` (see :ref:`figure 1 <segmenting_data_smaller_units_fig1>`
below). In what follows, we will suppose that the string typed in
:ref:`Text Field` is *a simple example*.

.. _segmenting_data_smaller_units_fig1:

.. figure:: figures/segment_example_schema.png
    :align: center
    :alt: Schema illustrating the usage of widget Segment

    Figure 1: A schema for testing the :ref:`Segment` widget
    
In its basic form (i.e. with **Advanced settings** unchecked, see
:ref:`figure 2 <segmenting_data_smaller_units_fig2>` below),
:ref:`Segment` offers four parameters in the drop-down menu named segment type. The string can be segmented into lines, letters, words or using a regex. If chose, the widget then looks for all
matches of the regex pattern in each successive input segment, and creates for
every match a new segment in the output segmentation.

.. _segmenting_data_smaller_units_fig2:

.. figure:: figures/segment_example.png
    :align: center
    :alt: Interface of widget Segment configured with regex "\w+"

    Figure 2: Interface of the :ref:`Segment` widget, configured for word segmentation

For instance, the regex ``\w+`` divides each incoming segment into sequences
of alphanumeric character (and underscore)--which in our case amounts to
segmenting *a simple example* into three words. To obtain a segmentation
into letters (or to be precise, alphanumeric characters or underscores),
simply use ``\w``.

Of course, queries can be more specific. If the relevant unit is the word,
regexes will often use the ``\b`` *anchor*, which represents a word boundary.
For instance, words that contain less than 4 characters can be retrieved
with ``\b\w{1,3}\b``, those ending in *-tion* with ``\b\w+tion\b``, and the
inflected forms of *retrieve* with ``\bretriev(e|es|ed|ing)\b``.

With the Advanced settings checked (see figure 3 below), several regexes can be added to the list. Regexes can be tokenized or splited, depending on your research goal. For more information, see 
:ref:`Segment widget <Segment>`

.. figure:: figures/segment_advanced_example.png

See also
--------

* :ref:`Reference: Segment widget <Segment>`
* :doc:`Cookbook: Segment text in smaller units <segment_text>`
