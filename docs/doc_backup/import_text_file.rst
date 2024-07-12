.. meta::
   :description: Orange Textable documentation, cookbook, import text from
                 file
   :keywords: Orange, Textable, documentation, cookbook, import, text,
              file

Import text from file
=====================

Goal
----

Import the content of one or more raw text files for further processing with
Orange Textable.

Ingredients
-----------

  ==============  =======
   **Widget**      :ref:`Text Files`
   **Icon**        |text_files_icon|
   **Quantity**    1
  ==============  =======

.. |text_files_icon| image:: figures/TextFiles_36.png

Procedure
---------

Single file
~~~~~~~~~~~

.. _import_text_file_fig1:

.. figure:: figures/text_files_basic_example.png
    :align: center
    :alt: Importing a file using the Text Files widget

    Figure 1: Importing the content of a file using the :ref:`Text Files` widget.

1. Create an instance of :ref:`Text Files` on the canvas.
2. Open its interface by double-clicking on the created instance.
3. Make sure the **Advanced settings** checkbox is *not* selected.
4. Click the **Browse** button to open the file selection dialog.
5. Select the file you want to import and close the file selection dialog by
   clicking **Ok**.
6. In the **Encoding** drop-down menu, select the encoding that corresponds to
   your file.
7. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
8. A segmentation covering the file's content is then available on the
   :ref:`Text Files` instance's output connections; to display or export it,
   see :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.
   
Multiple files
~~~~~~~~~~~~~~

.. _import_text_file_fig2:

.. figure:: figures/text_files_advanced_example.png
    :align: center
    :alt: Importing several files using the Text Files widget
    :scale: 80%

    Figure 2: Importing the content of several files using the :ref:`Text Files` widget.

1.  Create an instance of :ref:`Text Files` on the canvas.
2.  Open its interface by double-clicking on the created instance.
3.  Make sure the **Advanced settings** checkbox *is* selected.
4.  If needed, empty the list of imported files by clicking the **Clear all**
    button.
5.  Click the **Browse** button to open the file selection dialog.
6.  Select the first file you want to import. Select the encoding that corresponds to your file (if unknown, choose auto-detect in **Encoding** ) .
7.  Click the **Add** button to add your first file to the list of imported files. 
8.  Repeat steps 5 to 7 for adding all your files.  
  
9.  Click the **Send** button (or make sure the **Send automatically** checkbox is selected).
10. A segmentation containing a segment covering each imported file's content
    is then available on the :ref:`Text Files` instance's output connections;
    to display or export it, see :ref:`Cookbook: Text output
    <cookbook_toc_text_output_ref>`.

See also
--------

* :ref:`Reference: Text Files widget <Text Files>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

