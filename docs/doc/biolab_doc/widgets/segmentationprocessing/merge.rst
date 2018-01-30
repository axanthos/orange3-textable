Merge
=====

.. figure:: icons/merge.png

Merge two or more segmentations.

Signals
-------

**Inputs**:

-  Segmentation (multiple)

Any number of segmentations that should be merged together

**Outputs**:

-  Merged data

Merged segmentation

Description
-----------

The **Merge** widget merges two or more segmentations and outputs them to its output channel. 

.. figure:: images/merge-stamped.png

1. Create for each input segmentation an annotation whose value is the segmentation label and whose key is specified by the user in the text field on the right of the checkbox.

2. Automatically number the output segments and associate the number to the annotation key specified in the text field on the right. 

3. Copy every input segmentation annotation to the output segmentation.

4. Fuse several distinct segments with the same addresses into a single segment.

5. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

6. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Example
-------

We used the **Text Field** widget to input texts in three different languages. We renamed them according to the language that was used, merged them together by using the **Merge** widget and decided to import the labels with the key *Language*. We then displayed our results in the **Display** widget and by doing that we created ourselves a handy dictionary, which we then saved to our computer. 

.. figure:: images/merge-example.png