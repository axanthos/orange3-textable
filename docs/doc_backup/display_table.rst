.. meta::
   :description: Orange Textable documentation, cookbook, display table
   :keywords: Orange, Textable, documentation, cookbook, display, table

Display table
=============

Goal
----

Display an Orange Textable table.

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and possibly further processed (see
:ref:`Cookbook: Segmentation manipulation
<cookbook_toc_segmentation_manipulation_ref>`). A table has been created by
means of one of Orange Textable's :ref:`table construction widgets
<table_construction_widgets>` (see :ref:`Cookbook: Text analysis
<cookbook_toc_text_analysis_ref>`).

Ingredients
-----------

  ==============  ================  =======
   **Widget**      :ref:`Convert`    **Data Table**
   **Icon**        |convert_icon|    |datatable_icon|
   **Quantity**    1                 1
  ==============  ================  =======

.. |convert_icon| image:: figures/Convert_36.png
.. |datatable_icon| image:: figures/DataTable.png


Procedure
---------

.. _display_table_fig1:

.. figure:: figures/display_table_data_table_interface.png
   :align: center
   :alt: Convert to table format with an instance of Convert and Data Table
   :scale: 80%
   
   Figure 1: Display an Orange Textable table with instances of
   :ref:`Convert` and **Data Table**.

1. Create an instance of :ref:`Convert` and **Data Table** on the canvas (the
   latter is found in the **Data** tab of Orange Canvas).
2. Drag and drop from the output connection (righthand side) of the widget
   instance that has been used to build a table (e.g. :ref:`Context`) to the
   :ref:`Convert` widget instance's input connection (lefthand side).
3. Connect the :ref:`Convert` instance to the **Data Table** instance.
4. Open the **Data Table** instance's interface by double-clicking on its
   icon on the canvas to display the table.
   
Comment
-------
   
* If the table is a frequency table, you may want to change its default
  orientation of the table to make it easier to read. To that effect, open the
  :ref:`Convert` instance's interface, tick the **Advanced settings**
  checkbox, and in the **Transform** section, tick the **transpose** checkbox.
  
.. _display_table_fig2:

.. figure:: figures/display_table_convert_interface.png
   :align: center
   :alt: Change the orientation of Orange Textable table using Convert

   Figure 2: Change the orientation of an Orange Textable frequency table
   using an instance of :ref:`Convert`.


See also
--------

* :doc:`Getting started: Converting between table formats
  <converting_table_formats>`
* :ref:`Reference: Convert widget <Convert>`
* :ref:`Reference: Table construction widgets <table_construction_widgets>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :ref:`Cookbook: Segmentation manipulation
  <cookbook_toc_segmentation_manipulation_ref>`
* :ref:`Cookbook: Text analysis <cookbook_toc_text_analysis_ref>`
