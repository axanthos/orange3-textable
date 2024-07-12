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
            "path":             "data\\Balzac\\Eugenie_Grandet.txt",
            "encoding":         "iso-8859-1",
            "annotation_key":   "auteur",
            "annotation_value": "Balzac"
        },
        {
            "path":             "data\\Balzac\\Le_Pere_Goriot.txt",
            "encoding":         "iso-8859-1",
            "annotation_key":   "auteur",
            "annotation_value": "Balzac"
        },
        {
            "path":             "data\\Daudet\\Lettres_de_mon_moulin.txt",
            "encoding":         "iso-8859-15",
            "annotation_key":   "auteur",
            "annotation_value": "Daudet"
        },
        {
            "path":             "data\\Daudet\\Tartarin_de_Tarascon.txt",
            "encoding":         "iso-8859-15",
            "annotation_key":   "auteur",
            "annotation_value": "Daudet"
        }
    ]
