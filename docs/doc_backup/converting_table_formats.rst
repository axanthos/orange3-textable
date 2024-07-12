.. meta::
   :description: Orange Textable documentation, converting between table
                 formats
   :keywords: Orange, Textable, documentation, table, format, conversion

Converting between table formats
================================

Orange Canvas has a "native" type for representing data tables, namely
*Table*. However, this type does not support Unicode well, which is a serious
limitation in the perspective of text processing. To overcome this issue (as
much as possible), Orange Textable defines its own Unicode-friendly table
representation format.

Every :ref:`table construction widget <table_construction_widgets>` in Orange
Textable emits data in the internal format of Orange Textable. Instances of
these widget must then be connected with an instance of :ref:`Convert`, which
has mainly two purposes:

    -   It *converts* data from Orange Textable's internal format to the
        native *Table* format of Orange Canvas, which makes it possible to
        use the other widgets of Orange Canvas for visualizing, modifying,
        analyzing, etc. tables built with Orange Textable.
        
    -   On demand, it *exports* data in *Table* format in tab-delimited
        format (either to a file or to the clipboard), typically in order to
        import them in a third-party data analysis software package; at the
        time of writing, this scenario is the only way to correctly visualize
        a table containing data encoded in Unicode.
        
As shown on :ref:`figure 1 <converting_table_formats_fig1>` below, section
**Encoding** of the widget's interface lets the user choose the encoding
of the *Table* object emitted by the widget (**Orange table**); variants of
Unicode should be avoided here since they are currently not well supported by
other widgets in Orange Canvas.

.. _converting_table_formats_fig1:

.. figure:: figures/convert_basic_example.png
    :align: center
    :alt: Basic interface of widget Convert

    Figure 1: Basic interface of widget :ref:`Convert`.

The encoding for text file export can also be selected in this section
(**Output file**); in this case there are no counter-indications to
the use of Unicode. Note that when exporting to the clipboard, the utf-8
encoding is used by default. Export proper is performed by clicking the
**Export** button and selecting the output file in the dialog that appears.

The take-home message here is this: when you create an instance of a
:ref:`table construction widget <table_construction_widgets>`, you may
systematically create a new instance of :ref:`Convert` and connect
them together. Usually, moreover, you will want to connect the
:ref:`Convert` instance to a *Data Table* instance (from the *Data*
tab of Orange Canvas) in order to view the table just built--except in the
case where it contains Unicode data that wouldn't display correctly in
*Data table*.

See also
--------

* :ref:`Reference: Convert widget <convert>`
* :ref:`Reference: Table construction widgets <table_construction_widgets>`
* :ref:`Cookbook: Table output <cookbook_toc_table_output_ref>`
