File list (Text Files widget)
================================

The keys (and associated values) for the file lists are the following:

.. csv-table::
    :header: "Key", *Type*, *Default*, *Value*, *Remark*
    :stub-columns: 1
    :widths: 2 1 1 2 3
   
    *path*,  *string*,  ---, *file path (absolute or relative)*, *be careful to escaping the backslash*
    *encoding*, *string*, ---, *file encoding*, *cf.* `Python doc (codecs) <http://docs.python.org/2/library/codecs.html#standard-encodings>`_
    *annotation_key*, *string*, ---, *annotation key*, ---
    *annotation_value*, *string*, "", *annotation value*, ---


Example::

    [
        {
            "path":             "data\\Shakespeare\\Romeo_and_Juliet.txt",
            "encoding":         "iso-8859-1",
            "annotation_key":   "author",
            "annotation_value": "Shakespeare"
        },
        {
            "path":             "data\\Shakespeare\\Hamlet.txt",
            "encoding":         "iso-8859-1",
            "annotation_key":   "author",
            "annotation_value": "Shakespeare"
        },
        {
            "path":             "data\\Dickens\\Oliver_Twist.txt",
            "encoding":         "iso-8859-15",
            "annotation_key":   "author",
            "annotation_value": "Dickens"
        },
        {
            "path":             "data\\Defoe\\Robinson_Crusoe.txt",
            "encoding":         "iso-8859-15",
            "annotation_key":   "author",
            "annotation_value": "Defoe"
        }
    ]
