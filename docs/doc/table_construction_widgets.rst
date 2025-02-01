.. meta::
   :description: Orange Textable documentation, table construction widgets
   :keywords: Orange, Textable, documentation, table, construction, widgets

Table construction widgets
==========================

Widgets of this category take *Segmentation* data in input and emit tabular
data in the internal format of Orange Textable. They are thus ultimately
responsible for converting text to tables, either by counting items
(:doc:`Count <count>`), by measuring their length (:doc:`Length <length>`), by quantifying
their diversity (:doc:`Variety <variety>`). Widget :doc:`Cooccurrence <cooccurrence>` makes
it possible to measure the tendency of text units to occur in the same contexts,
while :doc:`Context <context>` serves to build concordances and collocation lists.
Finally, :doc:`Category <category>` exploits categorical information associated with
segmentations.

.. toctree::
    :maxdepth: 1

    Count <count>
    Length <length>
    Variety <variety>
    Cooccurrence <cooccurrence>
    Context <context>
    Category <category>

