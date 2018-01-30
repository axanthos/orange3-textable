Intersect
=========

.. figure:: icons/intersect.png

In-/exclude segments based on another segmentation.

Signals
-------

**Inputs**:

-  Segmentation (multiple)

Segmentation out of which a subset of segments should be selected ("source" segmentation), or containing the segments that will be in-/excluded from the former ("filter" segmentation)

**Outputs**:

-  Selected data (default)

Segmentation containing the selected segments

-  Discarded data

Segmentation containing the discarded segments

Description
-----------

The **Intersect** widget enables the user to search through multiple segmentations and find segments that intersect. Those segments can then be included or excluded from the output segmentation. The widget is available in two versions, according to whether or not the *Advanced Settings* checkbox is selected.

The basic interface
-------------------

The basic interface allow the user to specify whether to include or exclude the intersecting segments from the output segmentation. 

.. figure:: images/intersect-basic-stamped.png

1. Select the widget mode you wish to use and include or exclude segments from the output segmentation. 

2. Use the drop-down menu to select the source and the filter segmentation. The latter is mostly used when trying to filter information deemed irrelevant for research. 

3. By clicking on the *Send* button, changes are committed to the output of the widget. Alternatively, use *Send automatically* and the segmentation will be modified on every change.

4. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted

The advanced interface
----------------------

.. figure:: images/intersect-advanced-stamped.png

1. Select the widget mode you wish to use and include or exclude segments from the output segmentation. 

2. & 4. Use the drop-down menu to select the source and the filter segmentation. The latter is mostly used when trying to filter information deemed irrelevant for research. 

3. & 5. A *Filter/Source annotation key* dropdown menu. If a given annotation key of the source/filter segmentation is selected, the corresponding annotation value (rather than content) types will condition the in-/exclusion of the source segmentation segments. 

6. Automatically number the segments from the output segmentation and associate the number to the annotation key specified in the text field on the right.

7. Copy every annotation from the input segmentation to the output segmentation.

8. By clicking on the *Send* button, changes are committed to the output of the widget. Alternatively, use *Send automatically* and the segmentation will be modified on every change.

9. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted

Example
------- 
For the purpose of this example, we have decided to explore the ratio between the lines spoken by male characters and the lines spoken by female characters in Shakespeare's `Romeo and Juliet <https://www.ibiblio.org/xml/examples/shakespeare/r_and_j.xml>`_. We used the **Extract XML** widget to extract all speaker tags (<SPEAKER>) and preprocessed the data because it was not all capitalized. We then divided the file into line segments. We used the **Text Field** widget to input the names of female characters in Romeo and Juliet and then segmented the segmentation into words. By using the **Intersect** widget and information about the segments sent to the widget's output we came to the conclusion that the ratio is approximately 2:1 in favor of male character lines.

.. figure:: images/intersect-example.png
