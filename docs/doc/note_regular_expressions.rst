.. meta::
   :description: Orange Textable documentation, note on regular expressions
   :keywords: Orange, Textable, documentation, regular expressions, regex

A note on regular expressions
=============================

Orange Textable widgets rely heavily on *regular expressions* (or
*regexes*), which are essentially a body of conventions for describing a
set of strings by means of a single string. These conventions are widely
documented in books and on the Internet, so we will not give here yet
another introduction to this topic. Nevertheless, a basic knowledge of
regexes is required to tap into the real potential of Orange Textable,
and more advanced knowledge to fully unleash it.

The syntax of regexes is partly standardized, but some variations
remain. Orange Textable uses Python regexes, for which Python
documentation is the best source of information. In particular, it
features a good `introduction to
regexes <https://docs.python.org/3/howto/regex.html>`__. A first reading
might be limited to the following sections:

- `Simple Patterns <https://docs.python.org/3/howto/regex.html#simple-patterns>`__
- `More Metacharaters <https://docs.python.org/3/howto/regex.html#more-metacharacters>`__

Also recommended are the following:

- `Compilation Flags <https://docs.python.org/3/howto/regex.html#compilation-flags>`__
- `Lookahead Assertions <https://docs.python.org/3/howto/regex.html#lookahead-assertions>`__
- `Greedy versus Non-Greedy <https://docs.python.org/3/howto/regex.html#greedy-versus-non-greedy>`__