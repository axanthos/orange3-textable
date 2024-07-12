.. meta::
   :description: Orange Textable documentation, cookbook, build a concordance
   :keywords: Orange, Textable, documentation, cookbook, concordance

Build a concordance
===================

Goal
----

Build a concordance to examine the context of occurrence of a given string.

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and possibly further processed (see
:ref:`Cookbook: Segmentation manipulation
<cookbook_toc_segmentation_manipulation_ref>`).

Ingredients
-----------

 ==============   ===============  =========
   **Widget**      :ref:`Segment`   :ref:`Context`
   **Icon**        |segment_icon|   |context_icon|
   **Quantity**    1                1
 ==============   ===============  =========

.. |segment_icon| image:: figures/Segment_36.png
.. |context_icon| image:: figures/Context_36.png

Procedure
---------

.. _build_concordance_fig1:

.. figure:: figures/build_concordance_interfaces.png
   :align: center
   :alt: Widgets used to build a concordance and their interfaces
   :scale: 80%

   Figure 1: Widgets used build a concordance and their interfaces
   
1. Create an instance of :ref:`Segment` and an instance of :ref:`Context` on
   the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation in which occurrences of the query
   string will be retrieved (e.g. :ref:`Text Field`) to the :ref:`Segment`
   widget instance's input connection (lefthand side).
3. Also connect both the :ref:`Text Field` instance and the :ref:`Segment`
   instance to the :ref:`Context` instance (thus forming a triangle).
4. Open the :ref:`Segment` instance's interface by double-clicking on its
   icon on the canvas and type the string whose context of occurrence will be
   examined in the **Regex** field (here: ``hobbit``); assign it a
   recognizable **Output segmentation label**, such as *key_segments* for
   instance.
5. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
6. Open the :ref:`Context` instance's interface by double-clicking on its
   icon on the canvas.
7. In the **Units** section, select the segmentation that contains the
   occurrences of the query string (here: *key_segments*) using the
   **Segmentation** drop-down menu.
8. In the **Contexts** section, choose **Mode: Containing segmentation**
   and select the segmentation that contains the original text (here:
   *text_string*, as emitted by the :ref:`Text Field` instance) using the
   **Segmentation** drop-down menu.
9. Tick the **Max. length** checkbox and set the maximum number of characters
   that should be displayed on either side of each occurrence of the query
   string.
10. Click the **Compute** button (or make sure the **Compute automatically**
    checkbox is selected).
11. A table showing the results is then available at the output connection of
    the :ref:`Count` instance; to display or export it, see :ref:`Cookbook:
    Table output <cookbook_toc_table_output_ref>`.

Comment
-------

* In the **Regex** field of the :ref:`Segment` widget you can use all the
  syntax of Python's regular expression (*cf.* `Python documentation
  <http://docs.python.org/library/re.html>`_); for instance, if you wish to
  restrict your search to entire words, you might frame the query string with
  word boundary anchors ``\b`` (in our example ``\bhobbit\b``).

See also
--------

* :ref:`Reference: Segment widget <Segment>`
* :ref:`Reference: Context widget <Context>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :ref:`Cookbook: Segmentation manipulation
  <cookbook_toc_segmentation_manipulation_ref>`
* :ref:`Cookbook: Table output <cookbook_toc_table_output_ref>`

