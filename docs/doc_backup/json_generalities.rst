Generalities
============

The general format of JSON configuration files is the following::

    [
        {
            "key_1": value_1,
            "key_2": value_2,
            ...
            "key_N": value_N
        },
        ...
        {
            "key_1": value_1,
            "key_2": value_2,
            ...
            "key_N": value_N
        }
    ]

NB:

* the file must be encoded in utf-8
* the whole file is included between square brackets ``[ ... ]``
* each entry of the list is included between braces ``{ ... }`` and separated
  from the next by a coma
* each entry contains a list of key--value pairs separated by comas, in an
  arbitrary order
* key and value are separated by a colon ``:``
* the key is always a string between double quotation marks ``"..."``
* the value may be a string between double quotation marks, or one of the
  Boolean keywords *true* and *false*
* inside each string, the backslash ``\`` and the double quotation marks ``"``
  must be preceded ("escaped") by a backslash; line break and tabulation are
  obtained with \n and \t respectively; the notation \uDDDD (where each D
  represents a digit) is accepted for Unicode characters.
* Certain keys have a default value and are thus optional; the others are
  compulsory.


