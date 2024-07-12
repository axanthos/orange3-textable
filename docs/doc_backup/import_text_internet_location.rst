.. meta::
   :description: Orange Textable documentation, cookbook, import text from
                 internet location
   :keywords: Orange, Textable, documentation, cookbook, import, text,
              internet location

Import text from internet location
==================================

Goal
----

Import text content located at one or more URLs for further processing with
Orange Textable.

Ingredients
-----------

  ==============  =======
   **Widget**      :ref:`URLs`
   **Icon**        |urls_icon|
   **Quantity**    1
  ==============  =======

.. |urls_icon| image:: figures/URLs_36.png

Procedure
---------

Single URL
~~~~~~~~~~

.. _import_text_internet_location_fig1:

.. figure:: figures/urls_basic_example.png
    :align: center
    :alt: Importing text from an internet location using the URLs widget

    Figure 1: Importing text from an internet location using the :ref:`URLs`
    widget.

1. Create an instance of :ref:`URLs` on the canvas.
2. Open its interface by double-clicking on the created instance.
3. Make sure the **Advanced settings** checkbox is *not* selected.
4. In the **URL** field, type the URL whose content you want to import
   (including the ``http://`` prefix).
5. In the **Encoding** drop-down menu, select the encoding that corresponds to
   this URL.
6. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
7. A segmentation covering the URL's content is then available on the
   :ref:`URLs` instance's output connections; to display or export it,
   see :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.
   
Multiple URLs
~~~~~~~~~~~~~

.. _import_text_internet_location_fig2:

.. figure:: figures/urls_advanced_example.png
    :align: center
    :alt: Importing text from several internet locations using the URLs widget
    :scale: 80%

    Figure 2: Importing text from several internet locations using the
    :ref:`URLs` widget.

1.  Create an instance of :ref:`URLs` on the canvas.
2.  Open its interface by double-clicking on the created instance.
3.  Make sure the **Advanced settings** checkbox *is* selected.
4.  If needed, empty the list of imported URLs by clicking the **Clear all**
    button.
5.  In the **URL(s)** field, enter the URLs you want to import (including the
    ``http://`` prefix), separated by the string " / " (space + slash +
    space); make sure they all have the same encoding (you will be able to add
    URLs that have other encodings later).
6.  In the **Encoding** drop-down menu, select the encoding that corresponds
    to the set of selected URLs.
7.  Click the **Add** button to add the set of selected URLs to the list of
    imported URLs.
8.  Repeat steps 5 to 7 for adding URLs in other encoding(s).
9.  Click the **Send** button (or make sure the **Send automatically**
    checkbox is selected).
10. A segmentation containing a segment covering each imported URL's content
    is then available on the :ref:`URLs` instance's output connections; to
    display or export it, see :ref:`Cookbook: Text output
    <cookbook_toc_text_output_ref>`.

See also
--------

* :ref:`Reference: URLs widget <URLs>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

