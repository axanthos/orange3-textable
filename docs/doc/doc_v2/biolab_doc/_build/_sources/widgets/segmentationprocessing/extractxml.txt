Extract XML
===========

.. figure:: icons/extractxml.png

Create a new segmentation based on XML markup.

Signals
-------

**Inputs**:

-  Segmentation

Segmentation covering XML data based on which a news segmentation will be created

**Outputs**:

-  Extracted data

Segmentation containing the segments corresponding to extracted XML elements

Description
-----------

The **Extract XML* widget is used to search portions corresponding to a specific `XML <https://en.wikipedia.org/wiki/XML>`_ element type in an input segmentation. It creates a segment for each occurence of this `element <http://www.w3schools.com/xml/xml_elements.asp>`_. If such an occurence is distributed among several segments of the input segmentation, the widget will create as many segments in the output segmentation. Every attribute from the extracted elements is automatically converted in and annotation in the output segmentation. The widget is available in two versions, according to whether or not the *Advanced Settings* checkbox is selected.

Basic interface
---------------

The basic interface only allows the extraction of a single type of element at a time; however, it extracts every occurrence of this element, including those embedded in other occurrences of the same type.

.. figure:: images/extractxml-basic-stamped.png

1. Delete the XML tags embedded within the extracted XML elements, if any. The extracted elements will potentially be decomposed in several segments corresponding to portions of their content, which are separated by the deleted XML tags. In the *XML* field, you select which element types are to be sought. 

2. By clicking on the *Send* button, changes are committed to the output of the widget. Alternatively, use *Send automatically* and the segmentation will be modified on every change.

3. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted

Advanced Interface
------------------

The advanced version of the **Extract XML** widget allows the user to configure the XML element extraction. 

.. figure:: images/extractxml-advanced-stamped.png

1. Indicate the XML element type which should be sought.

2. Assign to each output segment an annotation whose key is the text contained in the field immediately on the right and whose value is the name of the XML element extracted by the widget. 

3. Exclude XML tags embedded within the extracted XML elements from the output segmentation. The extracted elements will potentially be decomposed in several segments corresponding to portions of their content which are separated by the excluded XML tags. 

4. By not choosing this option, a single segment is created (as opposed to several).

5. Determines the behavior of the widget in the very particular case where (a) elements of the extracted type are (exactly) embedded in one another, (b) they have different values for the same attribute, (c) the *Remove markup* option is selected and (d) the *Fuse duplicates* option (section Options) as well.If the *Prioritize shallow attributes* option is selected, the value of the element closest to the “surface” will be kept. 

6. Limit the extraction by specifying the conditions bearing on attributes on the extracted elements. These conditions are expressed in the form of `regular expressions <https://en.wikipedia.org/wiki/Regular_expression>`_ that the given attribute values must match.

	- Use the buttons on the right side of the widget to delete the selected condition or completely empty the list.
	- Specify the attribute in question and the corresponding regular expression (RegEx).
	- Manage the application of the corresponding options to the regular expression. 
	- Add the newly created condition to the list.

7. Specify the output segmentation label:

 	- *Auto-number with key*: automatically number the segments of the output segmentation
 	- *Import annotations*: copy annotations from the input segmentation to the output segmentation
 	- *Merge duplicate segments*: fuse distinct segments with the same address

 8. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

 9. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Example
-------

We downloaded a set of Shakespeare's `plays <http://metalab.unc.edu/bosak/xml/eg/shaks200.zip>`_  marked up in XML and used the **Text Files** widget to import two files into Orange. We then extracted all stage directions by typing *<STAGEDIR>* in the XML element field. We are now free to explore how stage directions in a comedy differentiate from those in a tragedy. 

.. figure:: /images/extractxml-example.png






