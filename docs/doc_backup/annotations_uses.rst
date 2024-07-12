.. meta::
   :description: Orange Textable documentation, annotations and their uses
   :keywords: Orange, Textable, documentation, annotations, uses

Annotations and their uses
==========================

In Orange Textable, an *annotation* is a piece of information attached to a
segment. Annotations consist of two parts: *key* and *value*. For instance, in
the now classical case of the word segmentation of *a simple example*, segment
*example* could be associated with the annotation *{part of speech: noun}*;
this annotation's key is *part of speech* and its value is *noun*. The same
segment could be simultaneously associated with another annotation such as
*{word category: lexical}*, or any *{key: value}* pair deemed relevant.

Even though we have carefully ignored them so far, annotations play a
fundamental role in text data processing and analysis. They make it possible
to go beyond the basic level of forms that are "physically" present in a text
and tap into the more abstract--and often more interesting--level of the
*interpretation* of these forms.

For instance, the texts composing a given corpus could be annotated with
respect to their genre (*novel*, *short story*, and so on), and the parts of
these texts might be annotated with regard to their discourse type
(*narrative*, *description*, *dialogue*, and so on). Such data could be
exploited to study the distribution of discourse types as a function of genre,
which would be at best extremely difficult, if ever possible, without having
encoded the relevant information by means of annotations.

In the following sections, we will first see two simple methods for creating
or importing annotations in Orange Textable, and then various ways of
exploiting such annotations.

