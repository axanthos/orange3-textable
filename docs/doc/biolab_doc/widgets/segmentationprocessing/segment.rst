Segment
=======

.. figure:: icons/segment.png

Subdivide a segmentation using regular expressions.

Signals
-------

**Inputs**:

-  Segmentation

Segmentation that should be further segmented

- Message

JSON Message controlling the list of regular expressions

**Outputs**:

-  Segmented data

Segmentation containing the newly created segments

Description
-----------

The **Segment** widget subdivides a segmentation into a series of new segments by using regular expressions. Alternatively, it can also operate based on a desciption of the separators that appear in-between te segments. The user is also able to create annotations for the output segments. 

The interface of the widget is available in two versions, according to whether or not the *Advanced Settings* checkbox is selected.

Basic Interface
---------------

The basic interface of the widget only enables the application of a single regular expression.

.. figure:: images/segment-basic-stamped.png

1. Use the drop-down menu and define the segment type you need. There are several available options: *Segment into letters*, *Segment into words*, *Segment into lines*, and *Use a regular expression*. By choosing the latter, you need to input your own `RegEx <http://www.regular-expressions.info/tutorial.html>`_. 

2. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

3. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Advanced interface
------------------

In its advanced version, the widget enables the user to define several regular expressions and to determine the order in which they should successively be applied to each segment of the input segmentation. The user can also specify if a given regular expression describes the form of the targeted segments (*Tokenize* mode) or rather the form of the separators in-between these segments (*Split* mode). 

.. figure:: images/segment-advanced.png

1. Select the RegExes applied to each input segment and determine their application order. The list of RegExes with their associated modes, actual expressions, corresponding annotations and the options associated with those expressions appears on top of the window. 

2. The buttons on the left side of the *RegExes* section allow the user to modify his selection by:

	- changing the order in which the RegExes are applied: *Move Up*, *Move Down*
	- deleting individual RegExes from the list: *Remove*
	- clearing the list of all RegExes: *Clear All*
	- import a list of RegExes in JSON format and add it to the previously selected sources: *Import List*
	- export the list of RegExes in a JSON file: *Export List*

3. Select segmentation mode:

	- If you wish to use a regular expression to describe the form of the targeted segments, use the *Tokenize* mode. `Tokenization  <https://en.wikipedia.org/wiki/Tokenization_(lexical_analysis)>`_ is breaking a stream of text up into words, phrases, symbols, or other meaningful elements called tokens (an individual occurrence of a linguistic unit in speech or writing). 	
	- If you wish to use a regular expression to describe the form of the separators in-between these segments, use the *Split* mode. 

4. Specify the regular expression you wish to add. Optionally, also specify the annotation key and value. Control the application of the corresponding options to the regular expression: *Ignore case*, *Unicode dependent*, *Multiline*, *Dot matches*. 

5. Add the new regular expression to the list.

6. Define the output segmentation label:

	- *Auto-number with key*: automatically number the output segments and associate the number to the annotation key specified in the text field on the right.
	- *Import annotations*: copy the annotations of each input segment to the corresponding outpus segments.
	- *Fuse duplicate segments*: fuse several distinct segments with the same address into a single segment.

7. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 
	
8. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted
Example
-------

For the purpose of this example, we used the **Text Field** widget to input Shakespeare's `Sonnet 130 <http://www.shakespeare-online.com/sonnets/130.html>`_. We then connected it to the **Segment** widget and used a regular expression (\s+[^.!?]*[.!?]) to divide the poem into sentences. We later displayed it in the **Display** widget.

.. figure:: images/segment-example.png
