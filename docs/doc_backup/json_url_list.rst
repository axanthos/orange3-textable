URL list (URLs widget)
======================

The keys (and associated values) for the URLs lists are the following:

.. csv-table::
    :header: "Key", *Type*, *Default*, *Value*, *Remark*
    :stub-columns: 1
    :widths: 2 1 1 2 3
   
    *url*,  *string*,  ---, *file url (absolute)*, *be careful to include the indication* ``http://``
    *encoding*, *string*, ---, *file encoding*, *cf.* `Python doc (codecs) <http://docs.python.org/2/library/codecs.html#standard-encodings>`_
    *annotation_key*, *string*, ---, *annotation key*, ---
    *annotation_value*, *string*, "", *annotation value*, ---
 
Example::

    [
        {
            "url":              "http://www.imsdb.com/scripts/Alien.html",
            "encoding":         "iso-8859-1",
            "annotation_key":   "genre",
            "annotation_value": "sci-fi"
        },
        {
            "url":              "http://www.imsdb.com/scripts/Pulp-Fiction.html",
            "encoding":         "iso-8859-1",
            "annotation_key":   "genre",
            "annotation_value": "crime"
        }
    ]
