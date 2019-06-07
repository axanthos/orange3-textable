.. meta::
   :description: Orange Textable documentation homepage
   :keywords: Orange, Textable, documentation

.. only:: html

    .. image:: figures/banner.jpg
   
.. toctree::
   :maxdepth: 2

=============================
Orange Textable documentation
=============================

Welcome to the documentation of Orange Textable.

This documentation is divided in five main sections (see detailed `contents`_
below):

* The :doc:`Introduction <introduction>` offers a brief overview of what
  Orange Textable can do, as well as how it should be installed and
  configured. This is what you should read first if you are unsure whether
  Orange Textable is the right piece of software for your needs or how to set
  it up.

* Section :doc:`Getting started <getting_started>` is a tutorial that
  introduces the basic concepts underlying Orange Textable and its main usage
  patterns. This should be your first reading once you've determined that
  Orange Textable can be useful to you and installed it.

* In the :doc:`Cookbook <cookbook>` section, you'll find a number of concise,
  illustrated recipes describing how to perform various basic tasks with
  Orange Textable. When starting a new project, you might want to skim through
  this section in case some elementary operation you need is listed there.

* Section :doc:`Case studies <case_studies>` presents several illustrations of 
  the application of Orange Textable to more complex and interesting problems 
  in text data analysis.

* The :ref:`Widgets <widgets>` section is an exhaustive explanation of the role
  and effect of every component of Orange Textable's interface. The purpose of
  this part of the documentation is to help you find a specific piece of
  information about Orange Textable's operation when using it for your own
  projects.


Contents
========

.. toctree::
    :maxdepth: 2

    Introduction <introduction>

.. toctree::
    :maxdepth: 2

    Getting started <getting_started>

.. toctree::
    :maxdepth: 2

    Cookbook <cookbook>

.. toctree::
    :maxdepth: 2

    Case studies <case_studies>

.. _widgets:

Widgets
-------


.. _text_import_widgets:

Text Import
~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   widgets/text_field
   widgets/text_files
   widgets/urls
  

.. _segmentation_processing_widgets:

Segmentation Processing
~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   widgets/preprocess
   widgets/recode
   widgets/merge
   widgets/segment
   widgets/select
   widgets/intersect
   widgets/extract_xml
   widgets/display


.. _table_construction_widgets:

Table Construction
~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   widgets/count
   widgets/length
   widgets/variety
   widgets/cooccurrence
   widgets/context
   widgets/category
 

.. _conversion_export_widgets:

Conversion/Export 
~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 1

   widgets/convert
   widgets/message

   
.. _json_format:

JSON im-/export format
~~~~~~~~~~~~~~~~~~~~~~

Beyond a restricted number of sources, substitutions, or regular expressions,
it becomes tedious to configure instances of widgets :ref:`Text Files`,
:ref:`URLs`, :ref:`Recode`, and :ref:`Segment` using their advanced interface.
To alleviate this issue, these widgets enable the user to import or export
manually edited configuration lists in `JSON <http://www.json.org/>`_ format
as described in the following sections.

.. toctree::
    :maxdepth: 1

    Generalities <json_generalities>
    File list <json_file_list>
    URL list <json_url_list>
    Substitution list <json_substitution_list>
    Regular expression list <json_regular_expression_list>
