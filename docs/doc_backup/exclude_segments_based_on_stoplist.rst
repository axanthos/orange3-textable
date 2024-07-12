.. meta::
   :description: Orange Textable documentation, cookbook, exclude segments
                 based on a stoplist
   :keywords: Orange, Textable, documentation, cookbook, exclude, segments,
              stoplist, stopwords

Exclude segments based on a stoplist
====================================

Goal
----

Filter out segments based on a stoplist.

Prerequisites
-------------

Some text has been imported in Orange Textable (see :ref:`Cookbook: Text input
<cookbook_toc_text_input_ref>`) and it has been segmented into words (see
:doc:`Cookbook: Segment text in smaller units <segment_text>`).

Ingredients
-----------

  ==============  ==================  ===============  =======
   **Widget**      :ref:`Text Field`   :ref:`Segment`   :ref:`Intersect`
   **Icon**        |textfield_icon|    |segment_icon|   |intersect_icon|
   **Quantity**    1                   1                1
  ==============  ==================  ===============  =======

.. |textfield_icon| image:: figures/TextField_36.png
.. |segment_icon| image:: figures/Segment_36.png
.. |intersect_icon| image:: figures/intersect_36.png

Procedure
---------

.. _exclude_segments_based_on_stoplist_fig1:

.. figure:: figures/exclude_segments.png
   :align: center
   :alt: Exclude segments based on a stoplist with instances of Text Field,
         Segment and Intersect
   :scale: 80%

   Figure 1: Exclude segments based on a stoplist with instances of
   :ref:`Text Field`, :ref:`Segment` and :ref:`Intersect`
   
1. Create an instance of :ref:`Text Field` on the canvas and paste into it
   the stoplist you want to use.
2. Follow the indications given in :doc:`Cookbook: Segment text in smaller
   units <segment_text>` in order to segment the stoplist into words; in what
   follows, it is assumed that the label of the resulting segmentation is
   *stop words*.
3. Create an instance of :ref:`Intersect` on the canvas.
4. Drag and drop from the output connection (righthand side) of the widget
   instance that emits the segmentation to be filtered (here the top instance
   of :ref:`Segment`) to the :ref:`Intersect` instance's input connection
   (lefthand side).
5. Likewise, connect the :ref:`Segment` instance that emits the *stop words*
   segmentation to the :ref:`Intersect` instance.
6. Open the :ref:`Intersect` instance's interface by double-clicking on its
   icon on the canvas.
7. In the **Intersect** section, choose **Mode: Exclude**.
8. In the **Source segmentation** field, choose the label of the word
   segmentation to be filtered (here: *words*); in the **Filter segmentation**
   field, choose the label the segmentation containing the stopwords (here:
   *stop words*).
9. Click the **Send** button (or make sure the **Send automatically**
   checkbox is selected).
10. A segmentation containing the filtered segmentation is then available on
    the :ref:`Intersect` instance's output connections; to display or export
    it, see :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`.

   
Comment
-------

* Stopword lists for various languages can be found `here
  <http://members.unine.ch/jacques.savoy/clef/>`_.

See also
--------

* :doc:`Getting started: Using a segmentation to filter another
  <using_segmentation_filter_another>`
* :ref:`Reference: Intersect widget <Intersect>`
* :ref:`Cookbook: Text input <cookbook_toc_text_input_ref>`
* :doc:`Cookbook: Segment text in smaller units <segment_text>`
* :ref:`Cookbook: Text output <cookbook_toc_text_output_ref>`

