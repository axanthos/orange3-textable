Preprocess
==========

.. figure:: icons/preprocess.png

Basic text preprocessing.

Signals
-------

**Inputs**:

-  Segmentation

Segmentation covering the the text that should be preprocessed

**Outputs**:

-  Text data

Segmentation covering the modified text

Description
-----------

The **Preprocess* widget enables simple text preprocessing and creates a modified copy of the input content. The user can modify case (lower and upper) or replace accentuated characters with their non-accentuated equivalents.

.. figure:: images/preprocess-stamped.png

1. Change case and convert every character to lower or upper case.

2. Replace accentuated characters with their non-accentuated equivalents. 

3. Copy all the annotations of the input segmentation to the output segmentation. 

4. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

5. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

Example
-------

We used the **Text Field** widget to input a short text. We then decided to preprocess it in the **Preprocess** wiget and display it in the **Display** widget.

.. figure:: images/preprocess-example.png