.. meta::
   :description: Orange Textable documentation, Select widget
   :keywords: Orange, Textable, documentation, Select, widget

.. _Select:

Select
======

.. image:: figures/Select_54.png

Select a subset of segments in a segmentation.

Signals
-------

Inputs:

* ``Segmentation``

  Segmentation out of which a subset of segments should be selected

Outputs:

* ``Selected data`` (default)

  Segmentation containing the selected segments

* ``Discarded data``

  Segmentation containing the discarded segments

Description
-----------

This widget inputs a segmentation and creates a new segmentation including
only some of the input segments. Segment selection can be based on their
content, their annotations, or their frequency; it can also be random. No
matter which method is used, the widget emits on a second output connection
(not selected by default) a segmentation containing the segments that were
*not* selected.

The interface of **Select** is available in two versions, according to
whether or not the **Advanced Settings** checkbox is selected.

Basic interface
~~~~~~~~~~~~~~~

The basic version of the widget (see :ref:`figure 1 <select_fig1>` below) is
limited to the selection of segments based on a regular expression (see
`Method: Regex`_ in section `Advanced interface`_ below). The differences with
the advanced interface are the following: (i) regular expression options are
not accessible (*-u*, *Unicode dependent*, is nonetheless activated by
default); (ii) auto-numbering is disabled; and (iii) annotations are copied
by default.

.. _select_fig1:

.. figure:: figures/select_example.png
    :align: center
    :alt: Basic interface of the Select widget

    Figure 1: **Select** widget (basic interface).

Advanced interface
~~~~~~~~~~~~~~~~~~

In its advanced version, the **Select** section of the widget interface comes
in three versions depending on the value chosen in the **Method** drop-down
menu (see figures :ref:`2 <select_fig2>` to :ref:`4 <select_fig4>` below).

.. _select_fig2:

.. figure:: figures/select_advanced_regex_example.png
    :align: center
    :alt: Advanced interface of the Select widget (Regex method)

    Figure 2: **Select** widget (advanced interface, **Regex** method).

Method: Regex
*************

This method consists of selecting the segments of the input segmentation whose
content or annotations are matched by a regular expression. The **Mode**
drop-down menu (see :ref:`figure 2 <select_fig2>` above) allows the user to
specify if the segments corresponding to the regular expression should be
selected (**Include**) or not (**Exclude**), in which case the segments that
do *not* correspond to the regular expression will be selected.

The **Annotation key** drop-down menu allows the user to choose an annotation
key from the input segmentation; in that case, the segments whose annotation
values for this key are matched by the regular expression will be selected
(or not). If the value *(none)* is selected, the *content* of the segments
will be matched against the regular expression.

The **Regex** field is designed to specify the regular expression used for
segment selection, and the **Ignore case (i)**, **Unicode dependent (u)**,
**Multiline (m)** and **Dot matches all (s)** checkboxes control the
application of the corresponding options to this expression.

In the example of :ref:`figure 2 <select_fig2>` above, the widget is
configured to include (**Mode: Include**) from the input segmentation the
segments whose annotation value for key *category* (**Annotation key:**
*category*) is either *noun* or *verb* (**Regex:** ``^(noun|verb)$``).

Method: Sample
**************

This method consists of selecting the segments of the input segmentation with
a random sampling process, such that every input segment has the same
probability of being selected or not.

.. _select_fig3:

.. figure:: figures/select_advanced_sample_example.png
    :align: center
    :alt: Advanced interface of the Select widget (Sample method)

    Figure 3: **Select** widget (advanced interface, **Sample** method).

The **Sample size expressed as** drop-down menu (see :ref:`figure 3
<select_fig3>` above) allows the user to choose the way in which to express
the wanted size for the sample. If the value **Count** is selected, as on
:ref:`figure 3 <select_fig3>`, the size of the sample will be expressed
directly in the number of segments (**Sample size**). If the **Proportion**
value is selected, the size will be expressed in percentage of input segments
(**Sampling rate (%)**).

Method: Threshold
*****************

This method consists of retaining from the input segmentation only the
segments whose content (or annotation value for a given key) has a frequency
in the segmentation that is comprised between given bounds.

.. _select_fig4:

.. figure:: figures/select_advanced_threshold_example.png
    :align: center
    :alt: Advanced interface of the Select widget (Threshold method)

    Figure 4: **Select** widget (advanced interface, **Threshold** method).

The **Annotation key** drop-down menu (see :ref:`figure 4 <select_fig4>`
above) allows the user to select an annotation key from the input
segmentation; if so, the frequency of the annotation values associated with
this key will condition the inclusion of input segments. If the value *(none)*
is selected, the frequency of the segment *content* will be decisive.

The **Threshold expressed as** drop-down menu allows the user to choose the
way in which to express the minimal and maximal frequency limits. If the value
**Count** is selected, the limits will be expressed in absolute frequencies
(**Min./Max. count**). If the value **Proportion** is selected, as in
:ref:`figure 4 <select_fig4>`, the limits will be expressed in percentages
(**Min./Max. proportion (%)**). For both values (minimum and maximum),
thresholding is applied only if the corresponding box is checked.

In the :ref:`figure 4 <select_fig4>` example, the widget is configured to
retain only the segments whose annotation value for the key *category*
(**Annotation key**) has a relative frequency (**Threshold expressed as:
Proportion**) comprised between 5% (**Min. proportion (%)**) and 10% (**Max.
proportion (%)**) in the input segmentation.

The elements of the **Options** section of the widget interface are common to
the three selection methods presented above. The **Auto-number with key** checkbox enables the program
to automatically number the segments of the output segmentation and to
associate the number to the annotation key specified in the text field on the
right. The **Copy annotations** checkbox copies every annotation of the input
segmentation to the output segmentation.

The **Send** button triggers the emission of a segmentation to the output
connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation at every modification of its interface or when its input data are
modified (by deletion or addition of a connection, or because modified data is
received through an existing connection).

Below the **Send** button, some indications are given about the number of segments in the output
segmentation, or the reasons why no segmentation is emitted (no input data,
no selected input segment, etc.).

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
    interface (see `Warnings`_ and `Errors`_ below).

Warnings
~~~~~~~~

*No regex defined.*
    A regular expression must be entered in the **Regex** field in order for
    computation and data emission to proceed.

*No label was provided.*
    A label must be entered in the **Output segmentation label** field in
    order for computation and data emission to proceed.
    
*No annotation key was provided for auto-numbering.*
    The **Auto-number with key** checkbox has been selected and an annotation
    key must be specified in the text field on the right in order for
    computation and data emission to proceed.
    
Errors
~~~~~~

*Regex error: <error_message>.*
    The regular expression entered in the **Regex** field is invalid.
    
Examples
--------

* :doc:`Getting started: Partitioning segmentations
  <partitioning_segmentations>`
* :doc:`Getting started: Annotation-based selection
  <annotation_based_selection>`
* :doc:`Cookbook: Include/exclude segments based on a pattern
  <include_exclude_based_on_pattern>`
* :doc:`Cookbook: Filter segments based on their frequency
  <filter_segments_based_on_frequency>`
* :doc:`Cookbook: Create a random selection or sample of segments
  <random_sample>`

