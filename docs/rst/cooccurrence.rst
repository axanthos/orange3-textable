.. meta::
   :description: Orange Textable documentation, Cooccurrence widget
   :keywords: Orange, Textable, documentation, Count, widget

.. _Cooccurrence:

Cooccurrence
============

.. image:: figures/Cooccurrence_54.png

Measure the co-occurrence of segments in documents.

Signals
-------

Inputs:

* ``Segmentation`` (multiple)

  Segmentation whose segments constitute the units subject to measurement of their
  co-occurrence and the contexts in which the co-occurrence of the units will be measured

Outputs:

* ``Pivot Crosstab``

  Table displaying the co-occurrence of units in the defined context 

Description
-----------

This widget inputs one or several segmentations, measures the number of documents
in which the input segments occur simultaneously, and sends the result in the form
of a *co-occurrence matrix* [1]_.

The co-occurrence matrix produced by this widget is of *IntPivotCrosstab* type, 
a subtype of the generic *Table* format (see :ref:`Convert` widget, section :ref:`Table formats <anchor_to_table_formats>`). Since this table reflects a co-occurrence matrix,
the column and row types vary regarding the type of the defined context, both corresponding
to a *unit* type. The cell at the intersection of a given column and row represents
the number of documents (*context* types) in which these two *unit* types are occurred
simultaneously. As the measure of co-occurrence represents absolute frequency, the resulting
table contains integer numbers, and as such it is of *IntPivotCrosstab* type, a subclass
of *PivotCrosstab*.

To take a simple example, consider two segmentations of the string *a simple
example* [2]_:

A) label = *words*

===========  =======  =====  ==================  =================
 content      start    end    *part of speech*    *word category*
===========  =======  =====  ==================  =================
 *a*          1        1      *article*           *grammatical*
 *simple*     3        8      *adjective*         *lexical*
 *example*    10       16     *noun*              *lexical*
===========  =======  =====  ==================  =================

B) label = *letters* (extract)

=========  =======  =====  ===================
 content    start    end    *letter category*
=========  =======  =====  ===================
 *a*        1        1      *vowel*
 *s*        3        3      *consonant*
 *i*        4        4      *vowel*
 ...        ...      ...    ...
 *e*        16       16     *vowel*
=========  =======  =====  ===================

Typically, we could define unit types based on the content of the segments 
of the *letters* segmentation.

As for the context types, there are two distinct forms
of contexts for measuring the co-occurrence of the units:
* ``Sliding window`` 
* ``Containing segmentation`` 

The aforementioned modes are the Orange Textable offered ways to define contexts
while still using a single segmentation. 


*Sliding window* relies on the notion of a "window" of *n*
segments that we progressively "slide" from the beginning to the end of the
segmentation. In our example, by applying this principle to the *letters*
segmentation and by setting the window size to 3 segments, we thus define
the following contexts:

	1. *a si*
	2. *sim*
	3. *imp*
	4. *mpl*
	5. *ple*
	6. *le e*
	7. *e ex*
	8. *exa*
	9. *xam*
	10. *amp*
	11. *mpl*
	12. *ple*

Considering the letter segmentation as that of the unit types, we could obtain
the following co-occurrence matrix:

.. csv-table::
    :header: *__context__*, *a*, *s*, *i*, *m*, *p*, *l*, *e*, *x*
    :stub-columns: 1
    :widths: 1 1 1 1 1 1 1 1 1

    *a*,        4,    1,    1,    2,   1,    0,    1,    2
    *s*,        1,    2,    2,    1,   0,    0,    0,    0
    *i*,        1,    2,    3,    2,   1,    0,    0,    0
    *m*,        2,    1,    2,    6,   4,    2,    0,    1
    *p*,        1,    0,    1,    4,   6,    4,    2,    0
    *l*,        0,    0,    0,    2,   4,    5,    3,    0
    *e*,        1,    0,    0,    0,   2,    3,    5,    2
    *x*,        2,    0,    0,    1,   0,    0,    2,    3


Alternatively, we could consider the *annotation values* of the units and those
of the contexts instead of the content of the segmentations. For example, by defining
units based on the annotations associated to the key *letter category* in the
*letters* segmentation, and choosing the mode *Sliding window* for the context
with the window size of 3 (see Figure 1), we could obtain the following co-occurrence
matrix:


.. csv-table::
    :header: *__context__*, *vowel*, *consonant*
    :stub-columns: 1
    :widths: 3 2 3

    *vowel*,      10,    10
    *consonant*,      10,    12
  


The mode *Containing segmentation* consists of measuring the co-occurrence of
unit types segmentation in context types segmentation. In the above example we
consider *letter* as the segmentation for unit types and *word* as the segmentation
for context types, and thus the following co-occurrence matrix will be obtained
and is symmetric by definition[1]_:

.. csv-table::
    :header: *__context__*, *a*, *s*, *i*, *m*, *p*, *l*, *e*, *x*
    :stub-columns: 1
    :widths: 1 1 1 1 1 1 1 1 1

    *a*,        2,    0,    0,    1,   1,    1,    1,    1
    *s*,        0,    1,    1,    1,   1,    1,    1,    1
    *i*,        0,    1,    1,    1,   1,    1,    1,    1
    *m*,        1,    1,    1,    2,   2,    2,    2,    1
    *p*,        1,    1,    1,    2,   2,    2,    2,    1
    *l*,        1,    1,    1,    2,   2,    2,    2,    1
    *e*,        1,    1,    1,    2,   2,    2,    2,    1
    *x*,        1,    0,    0,    1,   1,    1,    1,    1
   

Each celll at the above table represents the number of words (segments of the
context types) in which the unit in the column and the unit in the row are
used simultaneously. For example, "2" in the fifth column and forth row, shows
that there are two words in which *p* has occurred at the same time with *m*.
    
It is possible to measure the co-occurrence of two distinct units in the given
context in the mode *Containing segmentation*. For instance it would be interesting
for us to know how many times a vowel and a consonant have occurred simoultanously 
in each word of the base segment. By checkmarking the ``Secondary units`` checkbox
in the interface of the widget, we will be asked to define a segmentation for the
secondary unit types. In this case, the associated co-occurrence matrix will no longer
be symmetric. Therefor, in the above example, vowels as the primary units segmentation
constitute the rows, and consonants as the secondary units segmentation constitute the
columns of the resulting co-occurrence matrix in *word* segmentation (see Figure 2):

.. csv-table::
    :header: *__context__*, *s*, *m*, *p*, *l*, *x*
    :stub-columns: 1
    :widths: 1 1 1 1 1 1

    *a*,        0,    1,    1,    1,   1
    *i*,        1,    1,    1,    1,   0
    *e*,        1,    2,    2,    2,   1

As mentioned in the *Sliding window* mode, it is always possible to measure the
co-occurrence of the annotation values of the units (primary and secondary) and those
of the contexts instead of the content of the segmentations. In the case of the above 
example with the secondary units, the resulting crosstab consists of only one cell
indicating the number of words in which every letter with *vowel*  and every letter
with *consonant* annotation value have been occurred at the same time:

.. csv-table::
    :header: *__context__*, *consonant*
    :stub-columns: 1
    :widths: 2 3

    *vowel*,      2


Note that it is up to the user to provide a coherent definition of the units
and contexts. In general, there are only three conditions to be met in this
respect: (a) the segment corresponding to the unit and the context are both
associated to the same string, (b) the initial position of the unit segment
in the string is higher or equal to that of the context segment, and (c) conversely
the final position of the unit is lower or equal to that of the context. In short,
the unit must be *contained* within the context.
    
It is also noteworthy that in order to measure the co-occurrence, it is by definition
necessary to specify a context, therefor unlike the Count widget, context specification
is not optional. The context is set to the *Sliding window* mode by default.

Finally, in every scenario considered here, we could also take an interest for the
co-occurrence of the sequences from 2, 3, ..., *n* segments  (or *n--grams*) rather
that to the frequency of isolated segments. Below the co-occurrence matrix of the
2-grams in the *Sliding window* mode with the window size 3 is illustrated:


.. csv-table::
    :header: *__context__*, *as*, *si*, *im*, *mp*, *pl*, *le*, *ee*, *ex*, *xa*, *am*
    :stub-columns: 1
    :widths: 1 1 1 1 1 1 1 1 1 1 1

    *as*,        1,    1,    0,    0,   0,    0,    0,    0,    0,    0
    *si*,        1,    2,    1,    0,   0,    0,    0,    0,    0,    0
    *im*,        0,    1,    2,    1,   0,    0,    0,    0,    0,    0
    *mp*,        0,    0,    1,    4,   2,    0,    0,    0,    0,    0
    *pl*,        0,    0,    0,    2,   4,    2,    0,    0,    0,    0
    *le*,        0,    0,    0,    0,   2,    3,    1,    0,    0,    0
    *ee*,        0,    0,    0,    0,   0,    1,    2,    1,    0,    0
    *ex*,        0,    0,    0,    0,   0,    0,    1,    2,    1,    0
    *xa*,        0,    0,    0,    0,   0,    0,    0,    1,    2,    1
    *am*,        0,    0,    0,    1,   0,    0,    0,    0,    1,    2


Hereafter the interface of the widget will be introduced (see
figures :ref:`1 <cooc_fig1>` to :ref:`4 <cooc_fig4>`). It contains three
separate sections for unit definition (**Units** and **Secondary units**) and
context definition (**Contexts**).

.. _cooc_fig1:

.. figure:: figures/cooc_example.png
    :align: center
    :alt: Cooccurrence widget in the default mode("Sliding window")

    Figure 1: **Cooccurrence** widget (**Sliding window** mode as the default mode).
    
In the **Units** section, the **Segmentation** drop-down menu allows the user
to select among the input segmentations, the one whose segment types will be subject 
to the co-occurrence measurement. The **Annotation key** menu displays
the annotation keys associated to the chosen segmentation, if any; if one of the
keys is selected, the corresponding annotation values will be considered; if on the
other hand the value *(none)* is selected, the *content* of the segments will be
taken into consideration. The **Sequence length** drop-down menu allows the user to
indicate if isolated segments or segment *n--grams* should be considered; in the
latter case, the (optional) string specified in the **Intra sequence delimiter**
text field will be used to separate the content or the annotation value corresponding to
each segment in the column headers [3]_.

The **Secondary units** section has almost the same characteristics of the **Units**
section, except the fact that there is no **Sequence length** menu. This section is
by default disabled due to the default mode of the **Contexts** section being *Sliding
window*, in which only one unit segmentation can be considered for the measure of
co-occurrence (see :ref:`figure 1 <cooc_fig1>`). When changing the mode to *Containing
segmentation*, the box becomes automatically enabled (see :ref:`figure 2 <cooc_fig2>`).

.. _cooc_fig2:

.. figure:: figures/cooc_secondary_units_example.png
    :align: center
    :alt: Secondary units box of Cooccurrence widget in mode "Sliding window"

    Figure 2: **Secondary units** box of **Cooccurrence** widget (**Sliding window** mode).


The **Contexts** section is available in two forms, depending on the
selected value in the **Mode** drop-down menu. This allows the user to
choose between the two possible ways of defining contexts described earlier.
The **Sliding window** mode (see :ref:`figure 3 <cooc_fig3>`) implements the
notion of a "sliding window" introduced earlier. Typically, it allows the user
to observe the co-occurrence of the unit types with one another throughout the
unit segmentation. The only parameter is the window size (in number of segments),
defined by the **Window size** cursor, set to 2 by default.

.. _cooc_fig3:

.. figure:: figures/cooc_mode_sliding_window_example.png
    :align: center
    :alt: Cooccurrence widget in mode "Sliding window"

    Figure 3: **Cooccurrence** widget (**Sliding window** mode).

.. _cooc_fig4:

.. figure:: figures/cooc_mode_containing_segmentation_example.png
    :align: center
    :alt: Cooccurrence widget in mode "Containing segmentation"

    Figure 4: **Cooccurrence** widget (**Containing segmentation** mode).

Finally, the **Containing segmentation** mode (see :ref:`figure 4
<cooc_fig4>`) corresponds to the case where contexts are defined by the
segment types that appear in a segmentation (which can be that of the units or
another). This segmentation, that we will call *context segmentation* by
analogy, is selected among the input segmentations by means of the
**Segmentation** drop-down menu. The **Annotation key** menu displays the
annotation keys associated with the context segmentation, if any; if one of
the keys is selected, the corresponding annotation value types will constitute
the row headers; otherwise the value *(none)* is selected so that *content* of
the segments will be exploited.

The **Info** section indicates whether or not the data is correctly sent to the
output table. If not, the respective error message will be given.

The **Compute** button triggers the emission of a table in the internal format
of Orange Textable, to the output connection(s). When it is selected, the
**Compute automatically** checkbox disables the button and the widget attempts
to automatically emit a segmentation at every modification of its interface or
when its input data are modified (by deletion or addition of a connection, or
because modified data is received through an existing connection).

Messages
--------

Information
~~~~~~~~~~~

*Data correctly sent to output.*
    This confirms that the widget has operated properly.

*Settings were* (or *Input has*) *changed, please click 'Compute' when ready.*
    Settings and/or input have changed but the **Compute automatically** 
    checkbox has not been selected, so the user is prompted to click the 
    **Compute** button (or equivalently check the box) in order for computation 
    and data emission to proceed.

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

*Resulting table is empty.*
    No table has been emitted because the widget instance couldn't find a
    single element in its input segmentation(s). A likely cause for this 
    problem (when using the **Containing segmentation** mode) is that the unit
    and context segmentations do not refer to the same strings, so that the 
    units are in effect *not* contained in the contexts. This is typically a
    consequence of the improper use of widgets :ref:`Preprocess` and/or
    :ref:`Recode` (see :ref:`anchor_to_caveat`).
        


See also
--------

* :ref:`Reference: Convert widget (section "Table formats")
  <anchor_to_table_formats>`

Footnotes
---------

.. [1] The definition  of co-occurrence may vary depending on the discipline in which 
       this notion is used. In text analytics, the co-occurrence is the number of
       the documents in which two textual units are simultanously occurred. Here by
       convention, co-occurrenec is the dot product of the transposed document-frequency
       matrix with itself, which is symmetric when considering only one unit type.
       Therefore, despite other definitions, the diagonal members of the matrix are not
       zero, rather indicate the frequency of the corresponding textual unit in the 
       context of interest.
.. [2] By convention, we do not indicate here the string index associated with
       each segment but only its start and end positions, along with the
       various annotation values associated with it; moreover, for the sake of
       readability, we do indicate the content of each segment, though it is
       not formally part of the segmentation (but rather of the string to
       which the segmentation refers).
.. [3] The first column header, *__context__*, is a name predefined by Orange
       Textable.
