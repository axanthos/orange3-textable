Select
======

.. figure:: icons/select.png

Select a subset of segments in a segmentation.

Signals
-------

**Inputs**:

-  Segmentation

Segmentation out of which a subset of segments should be selected

**Outputs**:

-  Selected data (default)

Segmentation containing the selected segments

-  Discarded data

Segmentation containing the discarded segments

Description
-----------

The **Segment** widget enables the user to select a subset of segments in segmentation. The selection is made by using regular expressions and the user can select whether to include or exclude the selected segments from the output segmentation. The widget is available in two versions, according to whether or not the *Advanced Settings* checkbox is selected.

The advanced version offers different methods of selection - Regex, Sample, or Threshold, whereas the basic version only offers specifying the selection by using regular expressions. 
The basic version of the widget also does not include regular expression options, auto-numbering is disabled and annotations are copied by default. 

Method: Regex
-------------

.. figure:: images/select-regex-stamped.png

1. Select a mode of selection: *Include* or *Exclude* the selected segment.

2. Specify the regular expression. Optionally, also specify the annotation key and value. Control the application of the corresponding options to the regular expression: *Ignore case*, *Unicode dependent*, *Multiline*, *Dot matches*

3. Select whether you wish to auto-nummber the segmentations and if you wish to copy the annotations from the input segmentation to the ouput of the widget. 

4. By clicking *Send* changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

5. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Method: Sample
--------------

.. figure:: images/select-sample-stamped.png

Select the segments of the input segmentation with a random sampling process. 

1. Choose in which way to express the wanted size for the sample.

	- *Count*: the size of the sample will be expressed directly in the number of segments.
	- *Proportion*: the sizze of the sample will be expressed in percentage of input segments

2. Select whether you wish to auto-number the segmentations and if you wish to copy the annotations from the input segmentation to the ouput of the widget. 

3. By clicking *Send* changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

4. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Method: Threshold
-----------------

.. figure:: images/select-treshhold-stamped.png

Only the segments whose content (or annotation value for a given key) has a frequency in the segmentation that is comprised between given bound are retained from the input segmentation.

1. Select an annotation key from the input segmentation.

2. Choose the way in which to express the minimal and maximal frequency limits:

 	- *Count*: the limits wll be expressed in absolute frequencies
 	- *Proportion*: the limits will be expressed in percentages

3. Select whether you wish to auto-number the segmentations and if you wish to copy the annotations from the input segmentation to the ouput of the widget. 

4. By clicking *Send* changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

5. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Example
-------

THRESHOLD NE DELA - javi rdeč error













Example
-------