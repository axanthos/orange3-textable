.. meta::
   :description: Orange Textable documentation, cookbook, replace all 
                 occurrences of a string or pattern
   :keywords: Orange, Textable, documentation, cookbook, replace, string,
              pattern

Replace all occurrences of a string/pattern
===========================================

Goal
----

Replace all occurrences of a string (or pattern) in a text with another
string.

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and possibly further processed (see
:ref:`Cookbook: Segmentation manipulation
<cookbook_toc_segmentation_manipulation_ref>`).

Ingredients
-----------

  ==============  =======
   **Widget**      :ref:`Recode`
   **Icon**        |recode_icon|
   **Quantity**    1
  ==============  =======

.. |recode_icon| image:: figures/Recode_36.png

Procedure
---------

.. _replace_all_occurrences_of_string_pattern_fig1:

.. figure:: figures/replace_all_occurrences_of_string_pattern.png
   :align: center
   :alt: Replace all occurrences of a string with the Recode widget

   Figure 1: Replace all occurrences of a string with an instance of
   :ref:`recode`.

1. Create an instance of :ref:`Recode` on the canvas.
2. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation to be modified (e.g.
   :ref:`Text Field`) to the :ref:`Recode` instance's input connection
   (lefthand side).
3. Open the :ref:`Recode` instance's interface by double-clicking on its
   icon on the canvas.
4. In the **Substitution** section, insert the string that will be replaced in
   the **Regex** field.
5. In the **Replacement string** field insert the replacement string.
6. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
7. A segmentation containing the modified text is then available on the
   :ref:`Recode` instance's output connections; to display or export it,
   see :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.

Comment
-------
* In the **Regex** field you can use all the syntax of Python's regular
  expression (*cf.* `Python documentation
  <http://docs.python.org/library/re.html>`_).
* In our example, we choose to replace all occurrences of British *-our* with
  American *-or* (for example, from *colour* to *color*); unless otherwise
  specified (typically using word boundary "anchor" ``\b``), replacements will
  also occur within words, i.e. *coloured* to *colored*.
 
  
See also
--------

* :ref:`Reference: Recode widget <recode>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :ref:`Cookbook: Segmentation manipulation
  <cookbook_toc_segmentation_manipulation_ref>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

