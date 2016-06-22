.. meta::
   :description: Orange Textable documentation, table construction widgets
   :keywords: Orange, Textable, documentation, table, construction, widgets

Table construction widgets
==========================

Widgets of this category take *Segmentation* data in input and emit tabular
data in the internal format of Orange Textable. They are thus ultimately
responsible for converting text to tables, either by counting items
(:ref:`Count`), by measuring their length (:ref:`Length`), by quantifying
their diversity (:ref:`Variety`). Widget :ref:`Cooccurrence` makes
it possible to measure the tendency of text units to occur in the same contexts,
while :ref:`Context` serves to build concordances and collocation lists.
Finally, :ref:`Category` exploits categorical information associated with
segmentations.

.. toctree::
    :maxdepth: 1

    Count <count>
    Length <length>
    Variety <variety>
    Cooccurrence <cooccurrence>
    Context <context>
    Category <category>

