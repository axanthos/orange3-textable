.. meta::
   :description: Orange Textable documentation, case study, Titus Andronicus
   :keywords: Orange, Textable, documentation, case study, Titus Andronicus, 
              stylometry, authorship

Stylometric analysis of Shakespeare's Titus Andronicus
======================================================

(This use case was designed with the help of `Douglas Duhaime 
<http://douglasduhaime.com/>`_ and the following text was slightly adapted from
a description kindly contributed by him.)

This is a case study in "stylometry", or the quantitative analysis of a 
writer's style. The data to be analyzed is William Shakespeare's play *Titus 
Andronicus*, which scholars have long believed William Shakespeare did not 
write alone. Since the publication of John Robertson's study *Did Shakespeare 
Write Titus Andronicus*, many have believed that particular scenes within the 
text have been written by other playwrights of the time: many believe that Act 
1 Scene 1, for instance, was written by Shakespeare's contemporary George 
Peele. 

In order to test this hypothesis, the following Orange Textable workflow 
measures the degree to which the language in each scene within *Titus 
Andronicus* resembles the language within each other scene (:ref:`figure 1 
<titus_andronicus_schema>` below). [#]_ By changing the **Mode** parameter 
within the **Intersect** instance, one can elect to focus only on content words 
or stopwords, and by changing the **Distance Metrics** parameter within the 
**Example Distance** isntance, one can change the similarity metric for the 
language comparison. Finally, by clicking on the **Distance Map** icon within 
this workflow, one can see at a glance how distinct the vocabulary within each 
scene is.

.. _titus_andronicus_schema:

.. figure:: figures/titus_andronicus_schema.png
    :align: center
    :scale: 75%
    :alt: Orange Textable workflow for the Titus Andronicus use case

    Figure 1: Orange Textable workflow for the stylometric analysis of *Titus Andronicus**.
    
Comparing the stopwords within each scene using a normalized Euclidean distance 
metric, one finds that Act 1 Scene 1 is indeed a significant outlier within 
*Titus Andronicus*. The scene remains an outlier when one performs TF-IDF 
normalization on the term-document matrix (within the **Convert** instance), 
and when one uses a normalized Manhattan distance metric. Iterating through 
each of the various distance metrics, and toggling between different 
normalization metrics, Act 1 Scene 1 remains the most consistent outlier. This 
adds further evidence to the argument that the scene's stylistic fingerprint 
departs from that of that of the rest of the play.

.. _titus_andronicus_map:

.. figure:: figures/titus_andronicus_map.png
    :align: center
    :scale: 75%
    :alt: Act 1 Scene 1 of Titus Andronicus is a consistent stylistic outlier.

    Figure 2: Act 1 Scene 1 is a consistent stylistic outlier in Shakespeare's play.    

.. [#] The schema can be downloaded from :download:`here
       <schemas/titus_andronicus_for_textable_v3.1.3.ows>`.
