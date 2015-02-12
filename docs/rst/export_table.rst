.. meta::
   :description: Orange Textable documentation, cookbook, export table
   :keywords: Orange, Textable, documentation, cookbook, export, table

Export table
=============

Goal
----

Export an Orange Textable table in a text file in order to later import it in
another program (e.g. spreadsheet software).

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and possibly further processed (see
:ref:`Cookbook: Segmentation manipulation
<cookbook_toc_segmentation_manipulation_ref>`). A table has been created by
means of one of Orange Textable's :doc:`table construction widgets
<table_construction_widgets>` (see :ref:`Cookbook: Text analysis
<cookbook_toc_text_analysis_ref>`).

Ingredients
-----------

  ==============  ================
   **Widget**      :ref:`Convert`
   **Icon**        |convert_icon|
   **Quantity**    1
  ==============  ================

.. |convert_icon| image:: figures/Convert_36.png

Procedure
---------

.. _export_table_fig1:

.. figure:: figures/export_table_convert_interface.png
   :align: center
   :alt: Export table with an instance of Convert

   Figure 1: Export table with an instance of :ref:`Convert`
   

1. Create an instance of :ref:`Convert` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that has been used to build a table (e.g. :ref:`Context`) to the
   :ref:`Convert` widget instance's input connection (lefthand side).
3. Open the :ref:`Convert` instance's interface by double-clicking on its
   icon on the canvas.
4. Select the desired encoding for the exported data (e.g. utf8).
5. Click the **Export to file** button to open the file selection dialog.
6. Select the location you want to export your file to and close the file 
   selection dialog by clicking on **Ok**.

Comment
-------

* If you rather want to *copy* the text content in order to later paste it in
  another program, click on **Copy to clipboard**; note that in this case, 
  the encoding is by default utf8 and cannot be changed.
* The default column delimiter is ``\t`` but this can be modified to either
  comma (``,``) or semi-colon (``;``) by ticking the **Advanced settings**
  checkbox in the :ref:`Convert` instance's interface, then selecting the
  desired delimiter in the **Column delimiter** drop-down menu (**Export**
  section).

See also
--------

* :ref:`Reference: Convert widget <Convert>`
* :doc:`Reference: Table construction widgets <table_construction_widgets>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :ref:`Cookbook: Segmentation manipulation
  <cookbook_toc_segmentation_manipulation_ref>`
* :ref:`Cookbook: Text analysis <cookbook_toc_text_analysis_ref>`
