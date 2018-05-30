
URLs
====

.. figure:: icons/urls.png

Fetch text data online.

Signals
-------

**Inputs**:

-  Message

JSON Message controlling the list of imported URLs

**Outputs**:

-  Text data

Segmentation covering the content of imported URLs

Description
-----------

The **URLs** widget is designed to import the contents of one or several internet locations (URLs) to the Orange Canvas softaware. Its output is a segmentation containing a (potentially annotated) segment for the content of each selected URL. The imported textual content is subject to normalization. The widget is available in two versions, according to whether or not the *Advanced Settings* checkbox is selected.

Basic interface
---------------
The basic version limits the number of imported URLs to one. 

.. figure:: images/urls-basic-stamped.png

1. Input the selected URL and select the encoding of its content.

2. By clicking *Send* changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

3. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Advanced interface
------------------

The advanced version of the **URLs** widget allows the user to import the content of several URLs in a determined order; each URL can moreover be associated to a distinct encoding and specific annotations. The emitted segmentation contains a segment for the content of each imported URL.

1. The *Sources* section allows the user to select the imported URLs as well as their content's encoding, to determine the order in which they appear in the output segmentation, and optionally assign annotations. The list of imported URLs with additional information about corresponding annotations and encodings appears at the top of the window. 
	
2. The buttons on the left side of the *Sources* section allow the user to modify their selection by:

	a) changing the order in which the URLs appear in the output: *Move Up*, *Move Down*
	b) deleting individual URLs from the list: *Remove*
	c) clearing the list of all URLs: *Clear All*
	c) import a list of URLs in JSON format and add it to the previously selected sources: *Import List*
	d) export the source list in a JSON file: *Export List*

3. Add new URLs to the list. They must first be input in the field before they can be added to the list by clicking on the *Add* button. If you wish to add several URLs simultaneously, you must separate them by the string " / " (space + slash +space).

4. Select the *Encoding*.

5. Assign an annotation by specifying its key in the *Annotation key* field and the corresponding value in the *Annotation value* field. These three parameters (encoding, key, value) will be applied to each URL appearing in the URLs field at the moment of their addition to the list with *Add*.

6. Specify the label affected to the output segmentation. The *Import URLs with key* checkbox enables the program to create for each imported URL an annotation whose value is the file name (as displayed in the list) and whose key is specified by the user in the text field on the right of the checkbox. Similarly, the button *Auto-number with key* enables the program to automatically number the imported URLs and to associate the number to the annotation key specified in the text field on the right.

7. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

8. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Example
-------

For the purpose of this example, we have decided to make use of the advanced interface and explore the additional options offered by it. 
We opened the **URLs** widget and selected the advanced settings option. We imported several URLs and annotated them. We got our data from the `Project Gutenberg <https://www.gutenberg.org/>`_ website and chose to focus on annotating Shakespeare's works by genre. We selected `Romeo and Juliet <http://www.gutenberg.org/cache/epub/1112/pg1112.txt>`_, `The Merchant of Venice <http://www.gutenberg.org/cache/epub/2243/pg2243.txt>`_ and Shakespeare's `Sonnets <http://www.gutenberg.org/cache/epub/1041/pg1041.txt>`_ and annotated them according to type (tragedy, comedy, poetry). We then displayed our results in the **Display** widget. 

.. figure:: images/urls-example.png













