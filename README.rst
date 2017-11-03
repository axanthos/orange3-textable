Textable
========

Textable is an open source add-on bringing advanced text-analytical
functionalities to the `Orange Canvas <http://orange.biolab.si/>`_ data mining
software package (itself open source). Look at the following `example
<http://orange-textable.readthedocs.io/en/latest/illustration.html>`_ to see
it in typical action.

The project's website is http://textable.io. It hosts a repository of
`recipes <http://textable.io/find-recipes>`_ to help you get started with
Textable.

Documentation is hosted at http://orange3-textable.readthedocs.io/ and
you can get further support at https://textable.freshdesk.com/ or by e-mail
to `support@textable.io <mailto:support@textable.io>`_

Orange Textable was designed and implemented by `LangTech Sarl
<http://langtech.ch>`_ on behalf of the `department of language and
information sciences (SLI) <http://www.unil.ch/sli>`_ at the `University of
Lausanne <http://www.unil.ch>`_ (see `Credits
<http://orange-textable.readthedocs.io/en/latest/credits.html>`_ and
`How to cite Orange Textable
<http://orange-textable.readthedocs.io/en/latest/credits.html>`_).

Features
--------

Basic text analysis
~~~~~~~~~~~~~~~~~~~

* use regular expressions to segment letters, words, sentences, etc. or full-text query
* use regexes to extract annotations from many input formats
* import in-line XML markup (e.g. TEI)
* include/exclude segments based on user-defined lists (stoplists)
* filter segments based on frequency
* easily generate random text samples

Advanced text analysis
~~~~~~~~~~~~~~~~~~~~~~

* concordances and collocations, also based on annotations
* segment distribution, document-term matrix, transition matrix, etc.
* co-occurrence tables, also between different types of segments
* lemmatization and POS-tagging via Treetagger
* robust linguistic complexity measures, incl. mean length of word, lexical diversity, etc.
* many advanced data mining algorithms: clustering, classification, factor analyses, etc.

Text recoding
~~~~~~~~~~~~~

* Unicode-aware preprocessing functions, e.g. remove accents from Ancient Greek text
* recode and restructure texts using regexes, e.g. rewrite CSV as XML

Extensibility
~~~~~~~~~~~~~

* handles hundreds of text files
* use Python script for custom text processing or to access external tools: NLTK, Pattern, GenSim, etc.

Interoperability
~~~~~~~~~~~~~~~~
* import text from keyboard, files, or URLs
* process any kind of raw text format: TXT, HTML, XML, CSV, etc.
* supports many text encodings, incl. Unicode
* export results in text files or copy-paste
* easy interfacing with Orange's Text Mining add-on

Ease of access
~~~~~~~~~~~~~~

* user-friendly visual interface
* ready-made recipes for a range of frequent use cases
* extensive documentation
* support and community forums
