.. meta::
   :description: Orange Textable documentation, Message widget
   :keywords: Orange, Textable, documentation, Message, widget

.. _Message:

Message
=======

.. image:: figures/Message_54.png

Parse JSON data in segmentation and use them to control other widgets.

Signals
-------

Inputs:

* ``Segmentation``

  Segmentation containing a single segment with the JSON data to be parsed

Outputs:

* ``Message``

  *JSONMessage* object that can be sent to other widgets

Description
-----------

This widget inputs a segmentation containing a single segment whose content
is in `JSON <http://www.json.org/>`_ format. After validation, the data are
converted to a *JSONMessage* object and emitted to the widget's
output connections. Provided that the data conform to one of the formats
described in section :doc:`JSON im-/export format <json_format>`, the
*JSONMessage* object can be sent to an instance of the corresponding widget
(either :ref:`Text Files`, :ref:`URLs`, :ref:`Recode`, or :ref:`Segment`) and
used to control its behavior remotely.

.. _message_fig1:

.. figure:: figures/message_example.png
    :align: center
    :alt: Interface of the Message widget

    Figure 1: Interface of the **Message** widget.

The widget's interface offers no user-controlled option (see :ref:`figure 1
<message_fig1>` above). The **Info** section indicates the number of items
present in the parsed JSON data, or the reasons why no *JSONObject* can be
emitted (no input or invalid data, input segmentation containing more than one
segment).

The **Send** button triggers the emission of a **JSONMessage** object to the
output connection(s). When it is selected, the **Send automatically** checkbox
disables the button and the widget attempts to automatically emit a
segmentation when its input data are modified (by deletion or addition of a
connection, or because modified data is received through an existing
connection).

See also
--------

* :ref:`Reference: Text Files widget <Text Files>`,
  :ref:`text_files_remote_control_ref`
* :ref:`Reference: URLs widget <URLs>`, :ref:`urls_remote_control_ref`
* :ref:`Reference: Segment widget <Segment>`,
  :ref:`segment_remote_control_ref`
* :ref:`Reference: Recode widget <Recode>`, :ref:`recode_remote_control_ref`
* :doc:`Reference: JSON im-/export format <json_format>`
