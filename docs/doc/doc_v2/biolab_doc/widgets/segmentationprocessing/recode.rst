Recode
======

.. figure:: icons/recode.png

Custom text recoding using regular expressions.

Signals
-------

**Inputs**:

-  Segmentation

Segmentation covering the text that should be recoded

- Message

JSON Message controlling the list of substitutions

**Outputs**:

-  Recoded text data

Segmentation covering the recoded text

Description
-----------

The **Recode** widget creates a modified copy of the input segmentation. The modifications applied are defined by *substitutions*, namely pairs composed of a `regular expression <https://en.wikipedia.org/wiki/Regular_expression>`_  and a replacement string. The interface of the **Recode** widget is available in two versions, according to whether or not the *Advanced Settings* checkbox is selected.

Basic Interface
---------------

The basic version if the widget is limited to the application of a single substitution.

.. figure:: images/recode-basic-stamped.png

1. Specify the regular expression. Use regular expressions to reach more data or just enter a word you wish to subtitute. 

2. Specify the replacement string. If the replacement string is left empty, the text parts identified by the regular expression will simply be deleted. 

3. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 

4. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted.

Advanced Interface
------------------

The advanced interface allows the user to define several substitutions and to determine the order in which they should be applied.

.. figure:: images/recode-advanced-png 

1. The *Substitutions* section allows the user to select the substitutions applied to each successive input segment and to determine their application order. The list of substitutions with corresponding regular expressions, replacement strings and additional options associated with the regular expression used appears at the top of the window. 

2. The buttons on the left side of the *Sources* section allow the user to modify his selection by:

	- changing the order in which the substitutions are applied: *Move Up*, *Move Down*
	- deleting individual substitutions from the list: *Remove*
	- clearing the list of all substitutions: *Clear All*
	- import a list of substitutions in JSON format and add it to the previously selected sources: *Import List*
	- export the list of substitutions in a JSON file: *Export List*

3. Define a new subsitution by using RegEx.

4. Define the replacement string. 

5. Control the application of the corresponding options to the regular expression: *Ignore case*, *Unicode dependent*, *Multiline*, *Dot matches*. 

6. Add a new substitution to the list.

7. Copy every annotation of the input segmentation to the output segmentation. 

8. By clicking *Send*, changes are communicated to the output of the widget. Alternatively, tick *Send automatically* and changes will be communicated to the output at every modification. 
	
9. Information about the number of segments in the output segmentation or the reasons why no segmentation is emitted

Example
-------

For the purpose of this example, we have decided to adapt our American spelling for our readers that prefer British English. We mostly focused on the difference in spelling the affix *-ize* (or *-ise* that is preferred in British English). We used the **Text Field** widget to input several words that use the American way of spelling and then segmented the input segmentation into words. Lastly, we used the advanced interface of the **Recode** widget and replaced all occurences of the affix *-ize* with the affix *-ise*. 

.. figure:: images/recode-example.png













