Using a segmentation to filter another
======================================

In some cases, the number of forms to be selectively included in or excluded
from a segmentation is too large for using the :doc:`Select <select>` widget.
A typical example is the removal of "stopwords" from a text: in English for
instance, although the list of such words is finite, it is too long to try
to encode it by means of a regex (cf. `an example of such a list
<http://members.unine.ch/jacques.savoy/clef/englishST.txt>`_).

The purpose of widget :doc:`Intersect <intersect>` is precisely to solve that
kind of problem. It takes two segmentations in input and lets the user include
in or exclude from the first (*source*) segmentation those segments whose
content is the same as that of a segment in the second (*filter*)
segmentation. The widget's basic interface is shown on
:ref:`figure 1 <using_segmentation_filter_another_fig1>` below).

.. _using_segmentation_filter_another_fig1:

.. figure:: figures/intersect_example.png
    :align: center
    :alt: Interface of widget Intersect configured for stopword removal
    :figclass: align-center

    Figure 1: Interface of widget :doc:`Intersect <intersect>` configured for stopword removal.
    
Similarly to widget :doc:`Select <select>`, user must choose between modes
**Include** and **Exclude**. The next step is to specify which incoming
segmentation plays the role of the **Source** segmentation and the **Filter**
segmentation. (Here again, we will ignore the **Annotation key** option for
the time being.)

In order to try out the widget, set up a scheme similar to the one shown on
:ref:`figure 2 <using_segmentation_filter_another_fig2>` below). The first
instance of :doc:`Text Field <text_field>` contains the text to process (for
instance the
`Universal Declaration of Human Rights <http://www.un.org/en/documents/udhr/>`_),
while the second instance, *Text Field (1)*, contains the list of English
stopwords mentioned above. Both instances of :doc:`Segment <segment>` produce
a word segmentation with regex *\\w+*; the only difference in their
configuration is the output segmentation label , i.e. *words* for *Segment*
and *stopwords* for *Segment (1)*. Finally, the instance of
:doc:`Intersect <intersect>` is configured as shown on
:ref:`figure 1 <using_segmentation_filter_another_fig1>` above.

.. _using_segmentation_filter_another_fig2:

.. figure:: figures/intersect_example_scheme.png
    :align: center
    :alt: Scheme illustrating the use of the Intersect widget for stopword removal
    :figclass: align-center

    Figure 2: Example scheme for removing stopword using widget :doc:`Intersect <intersect>` .

The content of the first segments of the resulting segmentation is:

    *PREAMBLE*
    *Whereas*
    *recognition*
    *inherent*
    *dignity*
    *equal*
    *inalienable*
    *rights*
    *members*
    *human*
    *family*
    *foundation*
    *freedom*
    *justice*
    *peace*
    *world*
    ...


