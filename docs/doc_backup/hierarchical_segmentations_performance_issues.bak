.. meta::
   :description: Orange Textable documentation, hierarchical segmentations and
                 performance issues
   :keywords: Orange, Textable, documentation, hierarchical, segmentation,
              performance

Hierarchical segmentations and performance issues
=================================================

When widget :ref:`Segment` is applied to real, much longer texts
than *a simple example*, using such general regexes as ``\w+`` or ``\w`` may
result in the creation of a huge number of segments. Creating and manipulating
such segmentations can slow down excessively the execution of Orange Textable,
or even lead to memory overflow.

However, it is sometimes *necessary* to segment large texts into words or
letters, for instance in order to examine their frequency distribution. In
that case, if hardware allows it, a lot of time can be saved at the expense
of memory usage. Indeed, the cumulated time required to successively create
several ever more fine-grained segmentations (for instance into lines, then
words, then letters) is usually spectacularly shorter than the time required
to produce the most fine-grained segmentation directly (see :ref:`figure 1
<hierarchical_segmentations_performance_issues_fig1>` below).

.. _hierarchical_segmentations_performance_issues_fig1:

.. figure:: figures/chaining_segmentations.png
    :align: center
    :alt: chained hierarchical segmentations execute faster
    :scale: 80 %

    Figure 1: Chaining :ref:`Segment` instances to reduce execution time.

The situation is different when word or letter segmentation are conceived
as *intermediate steps* toward the creation of a segmentation containing only
selected words or letters. In that case, it is much more efficient (in memory
and execution time) to use a single instance of :ref:`Segment` with
a regex identifying only the desired words, as seen
:doc:`previously <segmenting_data_smaller_units>`
with the example of ``\bretriev(e|es|ed|ing)\b``.
