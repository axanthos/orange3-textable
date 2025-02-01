.. meta::
   :description: Orange Textable documentation, segmenting with regexes
   :keywords: Orange, Textable, documentation, segment, regex

Segmenting with regexes
=======================

This tutorial has already shown how to use the :doc:`Segment <segment>`
widget to segment text into words, letters, or lines thanks to the
drop-down menu options.

.. _segmenting_with_regexes_fig1:

.. figure:: figures/segmenting_with_regexes_fig1.png
    :align: center
    :alt: Interface of widget Segment configured with regex "\\w+"
    :scale: 80 %

    Figure 1: Interface of the :doc:`Segment <segment>` widget, configured for word segmentation

As a matter of fact, these options in the interface of :doc:`Segment <segment>` 
rely internally on the use of regular expressions. For instance, the **Segment 
into words** option uses regex ``\w+``. It divides each incoming segment into 
sequences of alphanumeric characters (and underscores)–which in our case amounts 
to segmenting *a simple example* into three words. Similarly, regex ``\w`` is 
used to obtain a segmentation into letters (or to be precise, alphanumeric 
characters or underscores).

With some knowledge of regular expressions, you can exploit the **Use a regular 
expression** option in the drop-down menu to do more specific queries. If the 
relevant unit is the word, regexes will often use the ``\b`` *anchor*, which 
represents a word boundary. For instance, words that contain less than 4 
characters can be retrieved with ``\b\w{1,3}\b``, those ending in *-tion* with 
``\b\w+tion\b``, and the inflected forms of *retrieve* with 
``\bretriev(e|es|ed|ing)\b``.

.. _segmenting_with_regexes_fig2:

.. figure:: figures/segmenting_with_regexes_fig2.png
    :align: center
    :alt: Interface of widget Segment configured with regex "\\b\\w{1,3}\\b"
    :scale: 80 %

    Figure 2: Using a Regular Expression (``\b\w{1,3}\b``) with the :doc:`Segment <segment>` widget

In these examples, the same result can be achieved by first using the
built-in **Segment into words** option and filtering the result with the
:doc:`Select <select>`
widget (see :doc:`Filtering segmentations using regexes <filtering_segmentations_regexes>`).
However, doing it in one step with
:doc:`Segment <segment>`
is more effective in terms of computation time. Besides, it makes it
possible to capture text fragments that are larger than words, e.g.
multi-word expressions.

To go further, you can add several regexes at the same time by ticking
the **Advanced settings** checkbox (see :ref:`figure 3 <segmenting_with_regexes_fig3>` below). Regexes can
then be used to describe the resulting tokens, as in the basic mode or,
depending on your research goal, to describe the delimiters occurring
between the resulting tokens (selecting mode **Split** instead of
**Tokenize**). For more information, see :doc:`Segment widget <segment>`.

.. _segmenting_with_regexes_fig3:

.. figure:: figures/segmenting_with_regexes_fig3.png
    :align: center
    :alt: Interface of widget Segment with Advanced Settings checked
    :scale: 80 %

    Figure 3: Interface of the :doc:`Segment <segment>` widget with **Advanced settings** checked

In several other widgets (:doc:`Text Files <text_files>`, :doc:`URLs <urls>`,
and :doc:`Recode <recode>`), **Advanced settings** also allows you to switch 
from a single manipulation to a series of operations. In most widgets, they give
access to additional useful options.

See also
-----------------

- :doc:`Textable's Basics: Segmenting data into smaller units <segmenting_data_smaller_units>`
- :doc:`Advanced Topics: Filtering segmentations using regexes <filtering_segmentations_regexes>`
- :doc:`Reference: Segment widget <segment>`
