Regular expression list (Segment widget)
========================================


The keys (and associated values) for the file lists are the following: 

.. csv-table::
    :header: "Key", *Type*, *Default*, *Value*, *Remark*
    :stub-columns: 1
    :widths: 2 1 1 2 3
   
    *mode*, *string*, ---, *"split" or "tokenize"*, ---
    *regex*,  *string*,  ---, *regular expression*, *be careful to escape the backslash*
    *ignore_case*, *Boolean*, *false*, *option -i*, *cf.* `Python doc (re.UNICODE) <http://docs.python.org/library/re.html#re.UNICODE>`_
    *multiline*, *Boolean*, *false*, *option -m*, *cf.* `Python doc (re.MULTILINE) <http://docs.python.org/library/re.html#re.MULTILINE>`_
    *dot_all*, *Boolean*, *false*, *option -s*, *cf.* `Python doc (re.DOTALL) <http://docs.python.org/library/re.html#re.DOTALL>`_
    *unicode_dependent*, *Boolean*, *false*, *option -u*, *cf.* `Python doc (re.IGNORECASE) <http://docs.python.org/library/re.html#re.IGNORECASE>`_
    *annotation_key*, *string*, ---, *annotation key*, ---
    *annotation_value*, *string*, "", *annotation value*, ---
  
Example::

    [
        {
            "mode":              "Tokenize",
            "regex":             ".",
            "dot_all":           true,
            "annotation_key":    "type",
            "annotation_value":  "other"
        },
        {
            "mode":              "Tokenize",
            "regex":             "\\w",
            "ignore_case":       true,
            "unicode_dependent": true,
            "annotation_key":    "type",
            "annotation_value":  "consonant"
        },
        {
            "mode":              "Tokenize",
            "regex":             "[aeiouy]",
            "ignore_case":       true,
            "annotation_key":    "type",
            "annotation_value":  "vowel"
        },
        {
            "mode":              "Tokenize",
            "regex":             "[0-9]",
            "annotation_key":    "type",
            "annotation_value":  "digit"
        }
    ]
