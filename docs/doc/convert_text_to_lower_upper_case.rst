Convert text to lower or upper case
=======================================

Goal
--------

Convert text to lower or upper case.

Prerequisites
-----------------

Some text has been imported in Orange Textable (see :doc:`Cookbook: Text input <text_input>`)
and possibly further processed (see :doc:`Cookbook: Segmentation manipulation <segmentation_manipulation>`).

Ingredients
---------------

  ==============  =======
   **Widget**      :doc:`Preprocess <preprocess>`
   **Icon**        |preprocess_icon|
   **Quantity**    1
  ==============  =======

.. |preprocess_icon| image:: figures/Preprocess_36.png

Procedure
-------------

.. _convert_text_lower_upper_case_fig1:

.. figure:: figures/convert_lower_upper_case.png
   :align: center
   :alt: Convert text to lower or upper case with an instance of Preprocess
   :scale: 75%

   Figure 1: Convert text to lower or upper case with an instance of 
   :doc:`Preprocess <preprocess>`.

1. Create an instance of :doc:`Preprocess <preprocess>`.

2. Drag and drop from the output (righthand side) of the widget that
   emits the segmentation to be modified, here :doc:`Text Field <text_field>`
   (*Hamlet*), to the input of :doc:`Preprocess <preprocess>`
   (lefthand side).

3. Double-click on the icon of :doc:`Preprocess <preprocess>`
   to open its interface.

4. In the **Processing** section, tick the **Transform case** checkbox.

5. Choose **to lower** or **to upper** in the drop-down menu on the
   right.

6. Click the **Send** button or tick the **Send automatically**
   checkbox.

7. A segmentation containing the modified text is then available at the
   output of :doc:`Preprocess <preprocess>`;
   to display or export it, see :doc:`Cookbook: Text output <text_output>`.

See also
------------

- :doc:`Reference: Preprocess widget <preprocess>`
- :doc:`Cookbook: Text input <text_input>`
- :doc:`Cookbook: Segmentation manipulation <segmentation_manipulation>`
- :doc:`Cookbook: Text output <text_output>`