Substitution list (Recode widget)
=================================

The keys (and associated values) for the file lists are the following:

.. csv-table::
    :header: "Key", *Type*, *Default*, *Value*, *Remark*
    :stub-columns: 1
    :widths: 2 1 2 2 3
   
    *regex*,  *string*,  ---, *regular expression*, *be careful to escape the slashes and backslash*
    *replacement_string*, *string*, *replacement string*, ---
    *ignore_case*, *Boolean*, *false*, *option -i*, *cf.* `Python doc (re.UNICODE) <http://docs.python.org/library/re.html#re.UNICODE>`_
    *multiline*, *Boolean*, *false*, *option -m*, *cf.* `Python doc (re.MULTILINE) <http://docs.python.org/library/re.html#re.MULTILINE>`_
    *dot_all*, *Boolean*, *false*, *option -s*, *cf.* `Python doc (re.DOTALL) <http://docs.python.org/library/re.html#re.DOTALL>`_
    *unicode_dependent*, *Boolean*, *false*, *option -u*, *cf.* `Python doc (re.IGNORECASE) <http://docs.python.org/library/re.html#re.IGNORECASE>`_
    
 
Example::

    [
        {
            "regex":              "<.+?>",
            "replacement_string": ""
        },
        {
            "regex":              "(behavi|col|neighb)our",
            "replacement_string": "&1or",
            "ignore_case":        true,
            "unicode_dependent":  true
        },
        {
            "regex":              "a (\\w+) of mine",
            "replacement_string": "my &1",
            "unicode_dependent":  true
        }
    ]
