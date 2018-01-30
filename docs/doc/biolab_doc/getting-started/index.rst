=========================
Orange Textable
=========================

Getting Started
===============

Orange Textable is an open-source add-on bringing advanced text-analytical functionalities to the Orange Canvas visual programming environment (itself open-source). It has been designed and implemented on behalf of the department of language and information sciences (SLI) at the University of Lausanne and it essentially enables users to build data tables on the basis of text data, by means of a flexible and intuitive interface. 
Orange Textable offers the following features:

   - text data import from keyboard, files, or URLs
   - support for various encodings, including Unicode
   - standard preprocessing and custom recoding (based on regular expressions)
   - segmentation and annotation of various text units (letters, words, etc.)
   - ability to extract and exploit XML-encoded annotations
   - automatic, random, or arbitrary selection of unit subsets
   - unit context examination using concordance and collocation tables
   - calculation of frequency and complexity measures
   - recoded text data and table export

This documentation is divided into 3 main sections (see detailed contents below):

- The **Getting Started** section provides an overview of the features in Orange Textable and gives relevant information on how to download and install the add-on and load your data.
- The **Widgets** section offers an exhaustive explanation of all widgets in the Orange Textable's interface. It also includes practical examples of usage.
- The **Tutorial** section shows how to use Orange Textable to solve more complex and interesting problems in text data analysis. The purpose of this part of the documentation is to inspire you to use Orange Textable for more advanced research. 


.. toctree::
   :maxdepth: 1

   getting-started/index


Widgets
=======

Text Import
-----------

.. toctree::
   :maxdepth: 1

   widgets/textimport/textfield
   widgets/textimport/textfiles
   widgets/textimport/urls
  

Segmentation Processing
-----------------------

.. toctree::
   :maxdepth: 1

   widgets/segmentationprocessing/preprocess
   widgets/segmentationprocessing/recode
   widgets/segmentationprocessing/merge
   widgets/segmentationprocessing/segment
   widgets/segmentationprocessing/select
   widgets/segmentationprocessing/intersect
   widgets/segmentationprocessing/extractxml
   widgets/segmentationprocessing/display


Table Construction
------------------

.. toctree::
   :maxdepth: 1

   widgets/tableconstruction/count
   widgets/tableconstruction/length
   widgets/tableconstruction/variety
   widgets/tableconstruction/cooccurrence
   widgets/tableconstruction/context
   widgets/tableconstruction/category
 

Conversion/Export 
-----------------

.. toctree::
   :maxdepth: 1

   widgets/conversionexport/convert
   widgets/conversionexport/message


Tutorials
=========

.. toctree::
   :maxdepth: 1

   tutorials/



.. toctree::
   :maxdepth: 1


