"""
Module TextableUtils.py
Copyright 2012-2016 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange-Textable package v2.0.

Orange-Textable v2.0 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange-Textable v2.0 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable v2.0. If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
Provides classes:
- SendButton
- AdvancedSettings
- InfoBox
- BasicOptionsBox
- JSONMessage
- VersionedSettingsHandlerMixin
- ContextInputListField
- SegmentationListContextHandler
- SegmentationContextHandler
- OWTextableBaseWidget
-----------------------------------------------------------------------------
Provides functions:
- pluralize
- updateMultipleInputs
- normalizeCarriageReturns
- getPredefinedEncodings
"""

__version__ = '0.12'

import re, os, uuid

from Orange.widgets import gui, settings, utils as widgetutils
from Orange.widgets.utils.buttons import VariableTextPushButton


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
        box = gui.hBox(self.widget, box=True, addSpace=False)
        autoSendCheckbox = gui.checkBox(
            widget=box,
            master=self.master,
            value=self.checkboxValue,
            label="",
            tooltip=u"Process and send data whenever settings change.",
        )
        autoSendCheckbox.setSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.Fixed)
        box.layout().addSpacing(10)
        sendButton = VariableTextPushButton(
            text=self.buttonLabel,
            default=True,
            toolTip=u"Process input data and send results to output.",
            textChoiceList=[self.buttonLabel, self.checkboxLabel],
        )

        if getattr(self.master, self.checkboxValue):
            sendButton.setText(self.checkboxLabel)

        sendButton.clicked.connect(self.callback)

        box.layout().addWidget(sendButton)

        autoSendCheckbox.disables.append((-1, sendButton))
        sendButton.setDisabled(autoSendCheckbox.isChecked())

        def sendOnToggle(state):
            # invoke send callback when autoSend checkbox is checked
            # and the master has the changed flag set
            if state and getattr(self.master, self.changedFlag, True):
                self.callback()

        def updateTextOnToggle(state):
            sendButton.setText(
                self.checkboxLabel if state else self.buttonLabel)

        autoSendCheckbox.toggled[bool].connect(sendOnToggle)
        autoSendCheckbox.toggled[bool].connect(updateTextOnToggle)

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
        gui.separator(
            widget=self.widget,
            height=1,
        )
        gui.checkBox(
            widget=self.widget,
            master=self.master,
            value=self.checkboxValue,
            label=u'Advanced settings',
            callback=self.callback,
            tooltip=(
                u"Toggle advanced settings on and off."
            ),
        )
        gui.separator(
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
        self.basicWidgets.append(gui.separator(
            widget=self.widget,
            height=height,
        ))

    def advancedWidgetsAppendSeparator(self, height=5):
        """Append a separator to the list of advanced widgets."""
        self.advancedWidgets.append(gui.separator(
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
        box = gui.widgetBox(
            widget=self.widget,
            #box=u'Widget state',
            box=False,
            orientation='vertical',
            addSpace=False,
        )
        gui.separator(widget=box, height=2)
        self.stateLabel = gui.widgetLabel(
            widget=box,
            label=u'',
        )
        self.stateLabel.setSizePolicy(QSizePolicy.Minimum,
                                      QSizePolicy.Preferred)
        self.stateLabel.setWordWrap(True)

        self.initialMessage()

    def setText(self, message='', state='ok'):
        """Format and display message"""
        self.widget.window().warning("")
        self.widget.window().error("")
        if state == 'ok':
            iconPath = self.okIconPath
        elif state == 'warning':
            iconPath = self.warningIconPath
            self.widget.window().warning(message)
        elif state == 'error':
            iconPath = self.errorIconPath
            self.widget.window().error(message)
        self.stateLabel.setText(
            "<html><img src='%s'>&nbsp;&nbsp;%s</html>" % (iconPath, message)
        )
        self.widget.window().adjustSizeWithTimer()

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
        if not self.widget.window().autoSend:
            self.setText(
                self.stringSettingsChanged + self.stringClickSend,
                state='warning',
            )

    def inputChanged(self):
        """Display 'Input changed' message"""
        if not self.widget.window().autoSend:
            self.setText(
                self.stringInputChanged + self.stringClickSend,
                state='warning',
            )


class BasicOptionsBox(object):
    """A class encapsulating the basic options box in Textable widgets"""

    def __new__(cls, widget, master, addSpace=False):
        """Initialize a new BasicOptionsBox instance"""
        basicOptionsBox = gui.widgetBox(
            widget=widget,
            box=u'Options',
            orientation='vertical',
            addSpace=addSpace,
        )
        gui.lineEdit(
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
        gui.separator(
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

from LTTL.Segmentation import Segmentation


class VersionedSettingsHandlerMixin(object):
    """
    A mixin to inject settings versioning into a settings.SettingsHandler

    It must precede the SettingsHandler in the bases list.

    Parameters
    ----------
    version : Optional[str]
        A version string matching a `re.compile(r'^(\d+)(\.\d+)+$')` pattern.

    Example
    -------
    >>> class VerSetHandler(VersionedSettingsHandlerMixin,
    ...                     settings.SettingsHandler):
    ...     pass

    """
    VERSION_KEY = "_TextableUtils_settings_version__"

    def __init__(self, *args, version=None, **kwargs):
        super().__init__(*args, **kwargs)
        if version is not None:
            if re.match(r"^(\d+)(\.\d+)+$", version):
                version = tuple(int(d) for d in version.split("."))
            else:
                raise ValueError("Invalid version string '{}'".format(version))
        self.__version = version  # type: Optional[Tuple[int, ...]]

    def pack_data(self, widget, *args, **kwargs):
        data = super().pack_data(widget, *args, **kwargs)
        if self.__version is not None:
            data[self.VERSION_KEY] = self.__version
        return data

    def initialize(self, instance, data=None, **kwargs):
        if data is not None and isinstance(data, dict):
            version = data.get(self.VERSION_KEY, None)
            if version != self.__version:
                data = None
            elif data is not None:
                data = data.copy()
                del data[self.VERSION_KEY]

        super().initialize(instance, data, **kwargs)

    def write_defaults_file(self, settings_file, *args, **kwargs):
        """Write defaults for this widget class to a file

        Parameters
        ----------
        settings_file : file-like object
        """
        self.defaults[self.VERSION_KEY] = self.__version
        try:
            super().write_defaults_file(settings_file)
        finally:
            del self.defaults[self.VERSION_KEY]

    def read_defaults_file(self, settings_file):
        """Read (global) defaults for this widget class from a file.

        Parameters
        ----------
        settings_file : file-like object
        """
        super().read_defaults_file(settings_file)

        version = self.defaults.get(self.VERSION_KEY, None)
        if version != self.__version:
            self.defaults = {}


class VersionedSettingsHandler(VersionedSettingsHandlerMixin,
                               settings.SettingsHandler):
    pass


class SegmentationsInputList(object):
    """
    A property descriptor for annotating a segmentations input list in a
    Textable widget.

    This class is used along with a SegmentationListContextHandler
    """
    def __init__(self):
        # name is filled in by SegmentationListContextHandler when it is
        # bound to the widget class.
        self.name = None

    def __get__(self, obj, objtype):
        if obj is not None:
            return obj.__dict__.setdefault("__segmentations", [])
        else:
            return self

    def __set__(self, obj, value):
        obj.__dict__["__segmentations"] = value


class SegmentationListContextHandler(VersionedSettingsHandlerMixin,
                                     settings.ContextHandler):
    """
    Segmentations list context handler.

    This Context handler matches settings on a list of
    (inputid, Segmentation) tuples as managed by :func:`updateMultipleInputs`.

    A class using this handler must define a single SegmentationsInputList
    property in its class namespace.

    Example
    -------
    >>> class Widget(OWTextableBaseWidget):
    ...     name = "Widget"
    ...     settingsHandler = SegmentationListContextHandler()
    ...     segmentations = SegmentationsInputList()
    ...
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputListFieldName = None
        self.inputListField = None

    def bind(self, widget_class):
        """
        Reimplemented from :class:`~settings.ContextHandler`.

        Bind settings handler instance to widget_class.

        Parameters
        ----------
        widget_class : class
        """
        super().bind(widget_class)

        # Search for a single instance of SegmentationsInputList in the
        # widget_class namespace and store it (also update/set it's name)
        segmentationlist = []
        for name in dir(widget_class):
            val = getattr(widget_class, name, None)
            if isinstance(val, SegmentationsInputList):
                segmentationlist.append((name, val))

        if len(segmentationlist) > 1:
            names = [name for name, _ in segmentationlist]
            raise TypeError(
                "A widget utilizing a SegmentationListContextHandler"
                "must declare a single SegmentationsInputList in it's class "
                "namespace (found {s},: {s})"
                .format(len(names), ", ".join(names))
            )
        elif len(segmentationlist) == 0:
            raise TypeError(
                "A widget utilizing a SegmentationListContextHandler"
                "must declare a SegmentationsInputList in it's class "
                "namespace."
            )
        elif segmentationlist:
            name, seglist = segmentationlist[0]
            seglist.name = name
            self.inputListField = seglist
            self.inputListFieldName = name

    def encode(self, widget, segmentationlist):
        """
        Encode a list of input segmentations for the receiving widget.

        Return a tuple of ```(widget.uuid, encoded_input)```.
        `encoded_input` is a list of  ```(label, annotations, uuid)```
        tuples where `label` is the segmentation label, `annotations` is
        a sorted tuple of segmentation annotation keys and `uuid` is the
        unique identifier of the input (source) widget.

       .. note::
            If the receiving widget does not have a uuid then the first
            element of the returned tuple (`widget.uuid`) will be None.

       :param widget.OWWidget widget:
            Widget receiving the input.
        :param list segmentationlist:
            List of (inputid, Segmentation) tuples.

        """
        def input_uuid(inputid):
            if isinstance(inputid, tuple) and len(inputid) >= 3:
                return getattr(inputid[2], "uuid", None)
            else:
                return None

        encoded = list()
        for inputid, segmentation in segmentationlist:
            label = segmentation.label
            annot = tuple(sorted(segmentation.get_annotation_keys()))
            uuid = input_uuid(inputid)
            encoded.append((label, annot, uuid))

        return (getattr(widget, "uuid", None), encoded)

    def new_context(self, widget_uuid, segmentations):
        context = super().new_context()
        _, inputs = self.encode(None, segmentations)
        context.encoded = (widget_uuid, inputs)
        return context

    def match(self, context, widget_uuid, inputsegmentations):
        """
        Match the `context` to the encoded input segmentations.

        Two contexts match if the receiving widget uuid matches the
        stored one and one input list encoding is a reordering of the
        other.

        """
        _, inputs = self.encode(None, inputsegmentations)
        stored_uuid, stored_inputs = context.encoded
        if stored_uuid != widget_uuid:
            # Receiving widget uuid does not match the stored context
            return 0

        try:
            _ = self._permutation(stored_inputs, inputs)
        except ValueError:
            pass
        else:
            # Perfect match on the inputs
            return 2

        # No match
        return 0

    def _permutation(self, seq1, seq2):
        if not (len(seq1) == len(seq2) and set(seq1) == set(seq2) and
                len(set(seq1)) == len(seq2)):
            raise ValueError
        return [seq1.index(el) for el in seq2]

    def settings_to_widget(self, widget):
        """
        Restore the saved `context` to `widget`.
        """
        super().settings_to_widget(widget)
        context = widget.current_context

        if context is None:
            return

        if self.inputListField and self.inputListFieldName in context.values:
            # find the permutation of the current input list so it matches
            # the stored one
            inputs = widgetutils.getdeepattr(widget, self.inputListFieldName)
            _, encoded = self.encode(widget, inputs)
            _, stored = context.encoded

            def uuids(seq):
                return [uuid for _, _, uuid in seq]

            # NOTE: Match on widget uuids only.
            # LTTL.Input.Input can change it's 'label' in place on user
            # interaction
            try:
                permutation = self._permutation(uuids(encoded), uuids(stored))
            except ValueError:
                permutation = range(len(inputs))

            permuted = [inputs[p] for p in permutation]

            # Restore the stored order in the widget.
            setattr(widget, self.inputListFieldName, permuted)

    def settings_from_widget(self, widget):
        """
        Get the settings from a widget.
        """
        super().settings_from_widget(widget)
        context = widget.current_context

        if context is None:
            return

        if self.inputListField:
            encoded = self.encode(
                widget, widgetutils.getdeepattr(widget, self.inputListFieldName)
            )
            context.encoded = encoded
            context.values[self.inputListFieldName] = encoded[1]


class SegmentationContextHandler(VersionedSettingsHandlerMixin,
                                 settings.ContextHandler):
    """
    Context handler for a single :class:`Segmentation` instance.

    This context handler matches settings on a single instance of
    :class:`Segmentation`. Two segmentations matche if they have the
    same label and annotation keys.
    """

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

    def new_context(self, segmentation):
        context = super().new_context()
        context.encoded = self.encode(segmentation)
        return context

    def match(self, context, *args):
        """
        Match the `context` to the encoded segmentation context.

        Two contexts match if their encodings are structurally
        equal (==).
        """
        assert len(args) == 1 and isinstance(args[0], Segmentation)
        return 2 if context.encoded == self.encode(*args) else 0


from Orange.widgets import widget
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import QTimer


class OWTextableBaseWidget(widget.OWWidget):
    """
    A base widget for other concrete orange-textable widgets.

    Defines s common `uuid` setting which is required for all Textable
    widgets.

    """

    #: Auto commit/send the output on any change
    autoSend = settings.Setting(False)  # type: bool
    #: A global widget unique id, for every widget created anew (i.e. not
    #: restored from a saved workflow) a new unique id is issued.
    uuid = settings.Setting(None, schema_only=True)  # type: str

    # Disable default OWWidget message bar
    # All in widget messages are delegated to InfoBox ??
    want_message_bar = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # uuid is None -> a new widget, otherwise it was restored from a
        # saved workflow
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())
        self.__firstShowPending = True
        # set size policy to Minimum to ensure that InfoBox statusLabel
        # receives enough space when its text is wrapped. A workaround
        # for OWWidget's layout not propagating `heightForWidth` size hints
        self.controlArea.setSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Minimum)

    def adjustSizeWithTimer(self):
        self.ensurePolished()
        if self.layout():
            self.layout().activate()
        QTimer.singleShot(0, self.adjustSize)

    def showEvent(self, event):
        if self.__firstShowPending:
            # Adjust to reasonable size at first show. Doing this here
            # ensures that 'AdvancedSettings' widgets get proper size/layout.
            self.__firstShowPending = False
            self.adjustSize()
        super().showEvent(event)

    def update_message_state(self):
        """
        Reimplemented.

        Disable the default OWWidget's message bar.
        """
        if self.want_message_bar:
            super().update_message_state()
