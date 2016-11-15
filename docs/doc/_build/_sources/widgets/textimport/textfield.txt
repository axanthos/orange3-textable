
Text Field
==========

.. figure:: icons/textfield.png

Import text data from keyboard input. 

Signals
-------

**Inputs**:

-  Text data

Segmentation containing the text to be edited

**Outputs**:

-  Text data

Segmentation covering the input text

Description
-----------

The **Text Field** widget enables the input of data by using a keyboard. It emits a segmentation containing a single unannotated segment covering the whole string. It can also be used to manually edit a previously imported string (imported from a text file or an URL). 

.. figure:: images/textfield-stamped.png

1. The editable text field. Standard editing functions (copy, paste, cancel, etc.) apply. 

2. By clicking *Send*, changes are committed to the output of the widget. Alternatively, tick *Send automatically* and changes will be committed at every modification. The text field's content is normalized in three ways: converted to Unicode, subjected to canonical Unicode-recomposition `technique <http://unicode.org/reports/tr15>`_, various forms of line endings (in particular \r\n and \r) are converted to a single form (namely \n). 

3. Information about the output: the length of the segmentation output in characters. 


Examples
--------

The first example is used to demonstrate how to input text for further processing by using the **Text Field** widget. The widget is fairly easy to use. Place the widget on the canvas by choosing it from the list of widgets in the add-on or use the right-click to click on the canvas and select the widget from there. Double-click on it to open it and input the text by using your keyboard. Standard editing functions apply and you can copy and paste text from other sources as well. When finished, click the *Send* button (alternatively, tick *Send automatically*) and display the segmented data through any of the compatible outputs. We simply entered the text string *This is a very simple example* and chose to display it in the **Display** widget. 

.. figure:: images/textfield-example-1.png

Our second example is used to demonstrate how to use the **Text Field** widget to manually edit imported strings of texts. 
We loaded Jane Austen's `Pride and Prejudice <http://www.gutenberg.org/cache/epub/1342/pg1342.txt>`_ by using the **URLs** widget and because the text about Project Gutenberg had no use for us (and our further research) we decided to remove it by editing the input content in the **Text Field** widget. 

.. figure:: images/textfield-example-2.png






