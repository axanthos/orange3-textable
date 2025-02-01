.. meta::
   :description: Orange Textable documentation, conversion and export widgets
   :keywords: Orange, Textable, documentation, conversion, export, widgets

Conversion/export widgets
=========================

The widgets of this category serve diverse purposes unified by the notion
of "conversion". :doc:`Convert <convert>` takes as input tabular data in Orange Textable
format and converts them to other formats, in particular the *Table* format
appropriate for further processing within Orange Canvas; :doc:`Convert <convert>` also
makes it possible to apply various standard transforms to a table, such as
sorting, normalizing, etc., as well as to export its contents in tab-delimited
text format. :doc:`Message <message>` takes as input a segmentation containing data in
a specific JSON format (see :doc:`Reference: JSON im-/export format <json_import_export>`)
and converts them to a "message" that can be used to control
the behavior of other widgets.

.. toctree::
    :maxdepth: 1

    Convert <convert>
    Message <message>


