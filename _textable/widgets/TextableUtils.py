"""
Module TextableUtils.py
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange-Textable package v1.6.

Orange-Textable v1.6 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange-Textable v1.6 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable v1.6. If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
Provides classes:
- SendButton
- AdvancedSettings
- InfoBox
- BasicOptionsBox
- JSONMessage
- ContextField
- ContextListField
- ContextInputListField
- ContextInputIndex
- SegmentationListContextHandler
- SegmentationContextHandler
-----------------------------------------------------------------------------
Provides functions:
- pluralize
- updateMultipleInputs
- normalizeCarriageReturns
- getPredefinedEncodings
- getWidgetUuid
"""

__version__ = '0.12'

import re, os, uuid, textwrap

from Orange.OrangeWidgets import OWGUI
from Orange.OrangeWidgets import OWContexts


class SendButton(object):
    """A class encapsulating send button operations in Textable"""

    def __init__(
        self,
        widget,
        master,
        callback,
        checkboxValue='autoSend',
        changedFlag='settingsChanged',
        buttonLabel=u'Send',
        checkboxLabel=u'Send automatically',
        infoBoxAttribute=None,
        sendIfPreCallback=None,
        sendIfPostCallback=None,
    ):
        """Initialize a new Send Button instance"""
        self.widget = widget
        self.master = master
        self.callback = callback
        self.checkboxValue = checkboxValue
        self.changedFlag = changedFlag
        self.buttonLabel = buttonLabel
        self.checkboxLabel = checkboxLabel
        self.infoBoxAttribute = infoBoxAttribute
        self.sendIfPreCallback = sendIfPreCallback
        self.sendIfPostCallback = sendIfPostCallback

    def draw(self):
        """Draw the send button and stopper on window"""
        sendButton = OWGUI.button(
            widget=self.widget,
            master=self.master,
            label=self.buttonLabel,
            callback=self.callback,
            tooltip=u"Process input data and send results to output.",
        )
        autoSendCheckbox = OWGUI.checkBox(
            widget=self.widget,
            master=self.master,
            value=self.checkboxValue,
            label=self.checkboxLabel,
            tooltip=u"Process and send data whenever settings change.",
        )
        OWGUI.setStopper(
            master=self.master,
            sendButton=sendButton,
            stopCheckbox=autoSendCheckbox,
            changedFlag=self.changedFlag,
            callback=self.callback,
        )
        self.resetSettingsChangedFlag()

    def sendIf(self):
        """Send data if autoSend is on, else register setting change"""
        if self.sendIfPreCallback is not None:
            self.sendIfPreCallback()
        if self.master.autoSend:
            self.callback()
        else:
            setattr(self.master, self.changedFlag, True)
        if self.sendIfPostCallback is not None:
            self.sendIfPostCallback()

    def settingsChanged(self):
        """Notify setting change and send (if autoSend)"""
        if self.infoBoxAttribute is not None:
            infoBox = getattr(self.master, self.infoBoxAttribute)
            infoBox.settingsChanged()
        self.sendIf()

    def resetSettingsChangedFlag(self):
        """Set master's settings change flag to False"""
        setattr(self.master, self.changedFlag, False)


class AdvancedSettings(object):
    """A class encapsulating advanced settings operations in Textable"""

    def __init__(
            self,
            widget,
            master,
            callback,
            checkboxValue='displayAdvancedSettings',
            basicWidgets=None,
            advancedWidgets=None,
    ):
        """Initialize a new advanced settings instance"""
        self.widget = widget
        self.master = master
        self.callback = callback
        self.checkboxValue = checkboxValue
        if basicWidgets is None:
            basicWidgets = list()
        self.basicWidgets = basicWidgets
        if advancedWidgets is None:
            advancedWidgets = list()
        self.advancedWidgets = advancedWidgets

    def draw(self):
        """Draw the advanced settings checkbox on window"""
        OWGUI.separator(
            widget=self.widget,
            height=1,
        )
        OWGUI.checkBox(
            widget=self.widget,
            master=self.master,
            value=self.checkboxValue,
            label=u'Advanced settings',
            callback=self.callback,
            tooltip=(
                u"Toggle advanced settings on and off."
            ),
        )
        OWGUI.separator(
            widget=self.widget,
            height=1,
        )

    def setVisible(self, bool):
        """Toggle between basic and advanced settings."""
        if bool:
            for widget in self.basicWidgets:
                widget.setVisible(not bool)
            for widget in self.advancedWidgets:
                widget.setVisible(bool)
        else:
            for widget in self.advancedWidgets:
                widget.setVisible(bool)
            for widget in self.basicWidgets:
                widget.setVisible(not bool)
        self.master.adjustSize()

    def basicWidgetsAppendSeparator(self, height=5):
        """Append a separator to the list of basic widgets."""
        self.basicWidgets.append(OWGUI.separator(
            widget=self.widget,
            height=height,
        ))

    def advancedWidgetsAppendSeparator(self, height=5):
        """Append a separator to the list of advanced widgets."""
        self.advancedWidgets.append(OWGUI.separator(
            widget=self.widget,
            height=height,
        ))


class InfoBox(object):
    """A class encapsulating info line management operations in Textable"""

    def __init__(
            self,
            widget,
            stringDataSent=u'Data correctly sent to output',
            stringNoDataSent=u'No data sent to output yet',
            stringSettingsChanged=u'Settings were changed',
            stringInputChanged=u'Input has changed',
            stringSeeWidgetState=u", see 'Widget state' below.",
            stringClickSend=u", please click 'Send' when ready.",
            wrappedWidth=30,
    ):
        """Initialize a new InfoBox instance"""
        self.widget = widget
        self.stringDataSent = stringDataSent
        self.stringNoDataSent = stringNoDataSent
        self.stringSettingsChanged = stringSettingsChanged
        self.stringInputChanged = stringInputChanged
        self.stringSeeWidgetState = stringSeeWidgetState
        self.stringClickSend = stringClickSend
        self.wrappedWidth = wrappedWidth

        # Path to icons...
        iconDir = os.path.join(
            os.path.split(os.path.split(os.path.abspath(__file__))[0])[0],
            'widgets',
            'icons',
        )
        self.okIconPath = os.path.join(iconDir, 'ok.png')
        self.warningIconPath = os.path.join(iconDir, 'warning.png')
        self.errorIconPath = os.path.join(iconDir, 'error.png')

    def draw(self):
        """Draw the InfoBox on window"""
        box = OWGUI.widgetBox(
            widget=self.widget,
            #box=u'Widget state',
            box=False,
            orientation='vertical',
            addSpace=False,
        )
        OWGUI.separator(widget=box, height=2)
        self.stateLabel = OWGUI.widgetLabel(
            widget=box,
            label=u'',
        )
        self.stateLabel.setWordWrap(True)
        self.initialMessage()

    def setText(self, message='', state='ok'):
        """Format and display message"""
        self.widget.topLevelWidget().warning(0)
        self.widget.topLevelWidget().error(0)
        if state == 'ok':
            iconPath = self.okIconPath
        elif state == 'warning':
            iconPath = self.warningIconPath
            self.widget.topLevelWidget().warning(0, message)
        elif state == 'error':
            iconPath = self.errorIconPath
            self.widget.topLevelWidget().error(0, message)
        self.stateLabel.setText(
            "<html><img src='%s'>&nbsp;&nbsp;%s</html>" % (iconPath, message)
        )
        self.widget.topLevelWidget().adjustSizeWithTimer()

    def initialMessage(self):
        """Display initial message"""
        self.setText(
            message=self.stringNoDataSent + self.stringClickSend,
            state='warning',
        )

    def dataSent(self, message=u''):
        """Display 'ok' message (and 'data sent' status)"""
        if message:
            self.setText(self.stringDataSent + ': ' + message)
        else:
            self.setText(self.stringDataSent + '.')

    def noDataSent(self, message=u'', warning=u'', error=u''):
        """Display error message (and 'no data sent' status)"""
        self.customMessage(message, warning, error, self.stringNoDataSent)

    def customMessage(self, message=u'', warning=u'', error=u'', pre=u''):
        """Display custom message"""
        if warning:
            mode = 'warning'
            completeMessage = pre + ": " + warning
        elif error:
            mode = 'error'
            completeMessage = pre + ": " + error
        elif message:
            mode = 'ok'
            completeMessage = pre + ": " + message
        else:
            mode = 'ok'
            completeMessage = pre + "."
        self.setText(completeMessage, mode)

    def settingsChanged(self):
        """Display 'Settings changed' message"""
        if not self.widget.topLevelWidget().autoSend:
            self.setText(
                self.stringSettingsChanged + self.stringClickSend,
                state='warning',
            )

    def inputChanged(self):
        """Display 'Input changed' message"""
        if not self.widget.topLevelWidget().autoSend:
            self.setText(
                self.stringInputChanged + self.stringClickSend,
                state='warning',
            )


class BasicOptionsBox(object):
    """A class encapsulating the basic options box in Textable widgets"""

    def __new__(cls, widget, master, addSpace=False):
        """Initialize a new BasicOptionsBox instance"""
        basicOptionsBox = OWGUI.widgetBox(
            widget=widget,
            box=u'Options',
            orientation='vertical',
            addSpace=addSpace,
        )
        OWGUI.lineEdit(
            widget=basicOptionsBox,
            master=master,
            value='label',
            orientation='horizontal',
            label=u'Output segmentation label:',
            labelWidth=180,
            callback=master.sendButton.settingsChanged,
            tooltip=(
                u"Label of the output segmentation."
            ),
        )
        OWGUI.separator(
            widget=basicOptionsBox,
            height=3,
        )
        return basicOptionsBox


class JSONMessage(object):
    """A class encapsulating a JSON message for inter-widget communication"""

    def __init__(
            self,
            content=u'',
    ):
        """Initialize a new JSON message instance"""
        self.content = content


def pluralize(
        input_string,
        criterion,
        plural=u's',
        singular=u'',
):
    """Replace every '@p' in a string with a given form (u's' by default) if
    some criterion is larger than 1, and by another form (u'' by default)
    otherwise.
    """
    replacement = plural if criterion > 1 else singular
    return re.compile(r'@p').sub(replacement, input_string)


def updateMultipleInputs(
        itemList,
        newItem,
        newId=None,
        removalCallback=None
):
    """Process input when the widget can take multiple ones"""
    ids = [x[0] for x in itemList]
    if not newItem:  # remove
        if not ids.count(newId):
            return  # no such item, removed before
        index = ids.index(newId)
        if removalCallback is not None:
            removalCallback(index)
        itemList.pop(index)
    else:
        if ids.count(newId):  # update (already seen item from this source)
            index = ids.index(newId)
            itemList[index] = (newId, newItem)
        else:  # add new
            itemList.append((newId, newItem))


def normalizeCarriageReturns(string):
    if os.name == 'nt':
        row_delimiter = u'\r\n'
    elif os.name == 'mac':
        row_delimiter = u'\r'
    else:
        row_delimiter = u'\n'
    return (string.replace('\n', row_delimiter))


def getPredefinedEncodings():
    """Return the list of predefined encodings"""
    return [
        u'ascii',
        u'iso-8859-1',
        u'iso-8859-15',
        u'utf-8',
        u'windows-1252',
        u'big5',
        u'big5hkscs',
        u'cp037',
        u'cp424',
        u'cp437',
        u'cp500',
        u'cp720',
        u'cp737',
        u'cp775',
        u'cp850',
        u'cp852',
        u'cp855',
        u'cp856',
        u'cp857',
        u'cp858',
        u'cp860',
        u'cp861',
        u'cp862',
        u'cp863',
        u'cp864',
        u'cp865',
        u'cp866',
        u'cp869',
        u'cp874',
        u'cp875',
        u'cp932',
        u'cp949',
        u'cp950',
        u'cp1006',
        u'cp1026',
        u'cp1140',
        u'cp1250',
        u'cp1251',
        u'cp1252',
        u'cp1253',
        u'cp1254',
        u'cp1255',
        u'cp1256',
        u'cp1257',
        u'cp1258',
        u'euc_jp',
        u'euc_jis_2004',
        u'euc_jisx0213',
        u'euc_kr',
        u'gb2312',
        u'gbk',
        u'gb18030',
        u'hz',
        u'iso2022_jp',
        u'iso2022_jp_1',
        u'iso2022_jp_2',
        u'iso2022_jp_2004',
        u'iso2022_jp_3',
        u'iso2022_jp_ext',
        u'iso2022_kr',
        u'latin_1',
        u'iso8859_2',
        u'iso8859_3',
        u'iso8859_4',
        u'iso8859_5',
        u'iso8859_6',
        u'iso8859_7',
        u'iso8859_8',
        u'iso8859_9',
        u'iso8859_10',
        u'iso8859_13',
        u'iso8859_14',
        u'iso8859_15',
        u'iso8859_16',
        u'johab',
        u'koi8_r',
        u'koi8_u',
        u'mac_cyrillic',
        u'mac_greek',
        u'mac_iceland',
        u'mac_latin2',
        u'mac_roman',
        u'mac_turkish',
        u'ptcp154',
        u'shift_jis',
        u'shift_jis_2004',
        u'shift_jisx0213',
        u'utf_32',
        u'utf_32_be',
        u'utf_32_le',
        u'utf_16',
        u'utf_16_be',
        u'utf_16_le',
        u'utf_7',
        u'utf_8',
        u'utf_8_sig'
    ]


# ============================
# Context dependent settings.
# ============================


class ContextField(object):
    """
    A simple field descriptor for storing a single value.

    :param str name: Attribute name in the widget to store.

    """

    def __init__(self, name):
        self.name = name

    def save(self, widget):
        """Return the value of the field from `widget`."""
        return widget.getdeepattr(self.name)

    def restore(self, widget, savedvalue):
        """Restore the `savedvalue` to `widget`."""
        setattr(widget, self.name, savedvalue)


class ContextListField(ContextField):
    """
    Context field for an item list with possible selection indices.

    This field descriptor can be used for storing a list of items
    (labels) and its selection state for a list view as constructed
    by :func:`OWGUI.listBox`

    :param str name:
        Attribute name of the item list in the widget (labels).
    :param str selected:
        Attribute name of a list of indices corresponding to
        selected items (default: `None` meaning there is no selection list).

    """

    def __init__(self, name, selected=None):
        ContextField.__init__(self, name)
        self.selected = selected

    def save(self, widget):
        """Return the value of the field from `widget`."""
        items = list(widget.getdeepattr(self.name))
        if self.selected is not None:
            selected = list(widget.getdeepattr(self.selected))
        else:
            selected = None
        return (items, selected)

    def restore(self, widget, savedvalue):
        """Restore the `savedvalue` to `widget`."""
        if len(savedvalue) == 2:
            items, selected = savedvalue
            setattr(widget, self.name, items)
            if self.selected is not None and selected is not None:
                setattr(widget, self.selected, selected)


class ContextInputListField(ContextField):
    """
    Context field for a list of 'Segmentations inputs'.

    This field describes a widget's input list (a list of
    (inputid, Segmentation) tuples as managed by for instance
    :func:`updateMultipleInputs`). In particular it stores/restores
    the order of the input list.

    :param name str: Attribute name in the widget.

    .. note::
        This field can only be used by :class:`SegmentationListContextHandler`

    .. warning::
        When the context is opened (:func:`OWWidget.openContext`) the input
        list order can be changed and assigned back to the widget. For
        instance the following code can raise an assertion error ::

            before = self.inputs
            self.openContext("", self.inputs)
            assert before == self.inputs

        However ``assert set(before) == set(self.inputs)`` will always
        succeed.

    """

    def __init__(self, name):
        ContextField.__init__(self, name)

    # Save/Restore requires the encoded context.
    def save(self, widget):
        raise NotImplementedError(
            "Save must be performed by the ContextHandler"
        )

    def restore(self, widget, savedvalue):
        raise NotImplementedError(
            "Restore must be performed by the ContextHandler"
        )


class ContextInputIndex(ContextField):
    """
    Context field for an index into the input Segmentations list.

    .. This is the same as :class:`ContextField`, but might be
       changed to support input index restore without permuting
       the input list (as done by `ContextInputListField`) and just
       change the stored index to point to the right item in the
       current list.

    """
    pass


class SegmentationListContextHandler(OWContexts.ContextHandler):
    """
    Segmentations list context handler.

    This Context handler matches settings on a list of
    (inputid, Segmentation) tuples as managed by for instance
    :func:`updateMultipleInputs`.

    :param str contextName: Context handler name.
    :param list fields:
        A list of :class:`ContextField`. As a convenience if the list
        contains any strings they are automatically converted to
        :class:`ContextField` instances.
    :param bool findImperfect:
        Unused, should always be the default ``False`` value (this parameter
        is only present for compatibility with the base class).

    """

    def __init__(self, contextName, fields=[], findImperfect=False, **kwargs):
        if findImperfect != False:
            raise ValueError("'findImperfect' is disabled")

        OWContexts.ContextHandler.__init__(
            self,
            contextName,
            findImperfect=False,
            syncWithGlobal=False,
            contextDataVersion=2,
            **kwargs
        )

        fields = [
            ContextField(field) if isinstance(field, str) else field
            for field in fields
            ]

        self.fields = fields

        # We store the ContextInputListField separately
        # (should it be passed as a separate argument?)
        self.inputListField = None
        inputListField = [
            field for field in fields
            if isinstance(field, ContextInputListField)
            ]
        if len(inputListField) == 1:
            self.inputListField = inputListField[0]
            self.fields.remove(self.inputListField)
        elif len(inputListField) > 1:
            raise ValueError("Only one 'ContextInputListField' is allowed")

    def findOrCreateContext(self, widget, items):
        encoded = self.encode(self, items)
        context, isnew = OWContexts.ContextHandler.findOrCreateContext(
            self, widget, encoded
        )

        # Store the encoded context
        context.encoded = encoded

        if isnew:
            context.values = dict()

        return context, isnew

    def encode(self, widget, segmentationlist):
        """
        Encode a list of input segmentations for the receiving widget.

        Return a tuple of ```(widget.uuid, encoded_input)```.
        `encoded_input` is a list of  ```(label, annotations, uuid)```
        tuples where `label` is the segmentation label, `annotations` is
        a sorted tuple of segmentation annotation keys and `uuid` is the
        unique identifier if the unique input (source) widget.

       .. note::
            If the receiving widget does not have a uuid then the first
            element of the returned tuple (`widget.uuid`) will be None.

       :param OWWidget widget:
            Widget receiving the input.
        :param list segmentationlist:
            List of (inputid, Segmentation) tuples.

        """
        encoded = list()
        for inputid, segmentation in segmentationlist:
            label = segmentation.label
            annot = tuple(sorted(segmentation.get_annotation_keys()))
            uuid = getattr(inputid[2], "uuid", None)
            encoded.append((label, annot, uuid))

        return (getattr(widget, "uuid", None), encoded)

    def match(self, context, imperfect, encoded):
        """
        Match the `context` to the encoded input segmentations.

        Two contexts match if the receiving widget uuid matches the
        stored one and one input list encoding is a reordering of the
        other.

        """
        widget_uuid, inputs = encoded
        stored_uuid, stored_inputs = context.encoded

        if stored_uuid != widget_uuid:
            # Receiving widget uuid does not match the stored context
            return 0

        if len(stored_inputs) == len(inputs):
            if set(stored_inputs) == set(inputs):
                # Perfect match on the inputs
                return 2
        # No match
        return 0

    def _permutation(self, seq1, seq2):
        assert len(seq1) == len(seq2) and set(seq1) == set(seq2)
        return [seq1.index(el) for el in seq2]

    def settingsToWidget(self, widget, context):
        """
        Restore the saved `context` to `widget`.
        """
        OWContexts.ContextHandler.settingsToWidget(self, widget, context)

        if self.inputListField and self.inputListField.name in context.values:
            # find the permutation of the current input list so it matches
            # the stored one
            inputs = widget.getdeepattr(self.inputListField.name)
            _, encoded = self.encode(widget, inputs)
            _, stored = context.values[self.inputListField.name]

            def uuids(seq):
                return [uuid for _, _, uuid in seq]

            # NOTE: Match on widget uuids only.
            # LTTL.Input.Input can change it's 'label' in place on user
            # interaction.
            permutation = self._permutation(uuids(encoded), uuids(stored))

            permuted = [inputs[p] for p in permutation]

            # Restore the stored order in the widget.
            setattr(widget, self.inputListField.name, permuted)

        for field in self.fields:
            if not field.name in context.values:
                continue
            field.restore(widget, context.values[field.name])

    def settingsFromWidget(self, widget, context):
        """
        Get the settings from a widget.
        """
        OWContexts.ContextHandler.settingsFromWidget(self, widget, context)

        if self.inputListField:
            inputs = self.encode(
                widget, widget.getdeepattr(self.inputListField.name)
            )
            context.values[self.inputListField.name] = inputs

        for field in self.fields:
            context.values[field.name] = field.save(widget)


class SegmentationContextHandler(OWContexts.ContextHandler):
    """
    Context handler for a single :class:`Segmentation` instance.

    This context handler matches settings on a single instance of
    :class:`Segmentation`. Two segmentations are matched if they
    have the same label and annotation keys.

    :param str contextName: Context handler name.
    :param list fields:
        A list of :class:`ContextField`. As a convenience if the list
        contains any strings they are automatically converted to
        :class:`ContextField` instances.
    :param bool findImperfect:
        Unused, should always be the default ``False`` value (this parameter
        is only present for compatibility with the base class).

    """

    def __init__(self, contextName, fields=[], findImperfect=False, **kwargs):
        if findImperfect != False:
            raise ValueError("'findImperfect' is not supported")

        OWContexts.ContextHandler.__init__(
            self,
            contextName,
            findImperfect=False,
            contextDataVersion=2,
            **kwargs
        )

        self.fields = [
            ContextField(field) if isinstance(field, str) else field
            for field in fields
            ]

    def encode(self, segmentation):
        """
        Encode a `Segmentation` instance.

        Return a (label, annotations) tuple where `label` is the
        segmentation label and `annotations` is a tuple of sorted
        annotations keys.

        """
        return (
            segmentation.label,
            tuple(sorted(segmentation.get_annotation_keys()))
        )

    def findOrCreateContext(self, widget, segmentation):
        encoded = self.encode(segmentation)
        context, isnew = OWContexts.ContextHandler.findOrCreateContext(
            self, widget, encoded
        )

        # Store the encoded context
        context.encoded = encoded

        if isnew:
            context.values = dict()

        return context, isnew

    def match(self, context, imperfect, encoded):
        """
        Match the `context` to the encoded segmentation context.

        Two contexts match if their encodings are structurally
        equal (==).

        """
        return 2 if context.encoded == encoded else 0

    def settingsToWidget(self, widget, context):
        for field in self.fields:
            if field.name in context.values:
                field.restore(widget, context.values[field.name])

    def settingsFromWidget(self, widget, context):
        for field in self.fields:
            context.values[field.name] = field.save(widget)


def getWidgetUuid(widget, uuid_name="uuid"):
    """
    Return a persistent universally unique id for a widget.

    :param widget: The OWWidget instance
    :param str uuid_name:
        Name of the uuid attribute (must be in widget's settingsList).

    .. note::
        This function should be called *after* `loadSettings()`.
        Follow this pattern in the widgets __init__ method::

            self.uuid = None
            self.loadSettings()
            self.uuid = getWidgetUuid(self, uuid_name="uuid")

    """
    # if the widget was loaded from a saved file then '_settingsFromSchema'
    # contains the saved settings otherwise the attribute is not present
    settings = getattr(widget, "_settingsFromSchema", None)
    if settings is not None and \
                    uuid_name in widget.settingsList and \
                    uuid_name in settings:
        # retrieve the stored uuid from the settings
        return settings[uuid_name]
    else:
        # A newly created widget gets a brand new uuid
        return uuid.uuid4()
