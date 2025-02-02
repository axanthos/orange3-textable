"""
Class OWTextableCooccurrence
Copyright 2012-2025 LangTech Sarl (info@langtech.ch)
-----------------------------------------------------------------------------
This file is part of the Orange3-Textable package.

Orange3-Textable is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3-Textable is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange3-Textable. If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = u'1.0.6'
__author__ = "Mahtab Mohammadi"
__maintainer__ = "LangTech Sarl"


import LTTL.ProcessorThread as Processor
from LTTL.TableThread import IntPivotCrosstab
from LTTL.Segmentation import Segmentation

from .TextableUtils import (
    OWTextableBaseWidget, ProgressBar,
    InfoBox, SendButton, updateMultipleInputs, pluralize,
    SegmentationListContextHandler, SegmentationsInputList,
    Task
)
import Orange.data
from Orange.widgets import widget, gui, settings

import re

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableCooccurrence(OWTextableBaseWidget):
    """Orange widget for calculating co-occurrences of text units"""

    name = "Cooccurrence"
    description = "Measure cooccurrence between segment types"
    icon = "icons/Cooccurrence.png"
    priority = 8005

    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [('Textable pivot crosstab', IntPivotCrosstab, widget.Default),
               ('Orange table', Orange.data.Table)]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    segmentations = SegmentationsInputList()  # type: list

    # Settings...
    intraSeqDelim = settings.Setting(u'#')
    units = settings.ContextSetting(-1)
    _contexts = settings.ContextSetting(-1)
    units2 = settings.ContextSetting(-1)
    mode = settings.ContextSetting(u'Sliding window')
    unitAnnotationKey = settings.ContextSetting(u'(none)')
    unit2AnnotationKey = settings.ContextSetting(u'(none)')
    contextAnnotationKey = settings.ContextSetting(u'(none)')
    coocWithUnits2 = settings.ContextSetting(False)
    sequenceLength = settings.ContextSetting(1)
    windowSize = settings.ContextSetting(2)

    want_main_area = False

    def __init__(self):
        """Initialize a Cooccurrence widget"""
        super().__init__()

        self.infoBox = InfoBox(
            widget=self.controlArea,
            stringClickSend=u", please click 'Send' when ready.",
        )
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually,
            infoBoxAttribute='infoBox',
            buttonLabel=u'Send',
            checkboxLabel=u'Send automatically',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Units box
        self.unitsBox = self.create_widgetbox(
            box=u'Units',
            orientation='vertical',
            addSpace=True,
            )

        self.unitsegmentationCombo = gui.comboBox(
            widget=self.unitsBox,
            master=self,
            value='units',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation for which the co-occurrences of\n"
                u"segments will be counted.\n"
                u"This defines the columns of the resulting crosstab,\n"
                u"as well as its rows if no secondary units are being used."
            ),
        )
        self.unitsegmentationCombo.setMinimumWidth(120)
        gui.separator(widget=self.unitsBox, height=3)
        self.unitAnnotationCombo = gui.comboBox(
            widget=self.unitsBox,
            master=self,
            value='unitAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicates whether the items whose co-occurrences will be\n"
                u"counted in the above specified segmentation\n"
                u"are defined by the segments' content (value 'none')\n"
                u"or by their annotation values for a specific\n"
                u"annotation key."
            ),
        )
        gui.separator(widget=self.unitsBox, height=3)
        self.sequenceLengthSpin = gui.spin(
            widget=self.unitsBox,
            master=self,
            value='sequenceLength',
            minv=1,
            maxv=1,
            step=1,
            orientation='horizontal',
            label=u'Sequence length:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"Indicates whether to count the co-occurrences of\n"
                u"single segments or rather of sequences of 2,\n"
                u"3, ... segments (n-grams).\n\n"
                u"Note that this parameter cannot be set to a\n"
                u"value larger than 1 if co-occurrences are to be\n"
                u"counted between primary and secondary units."
            ),
        )
        gui.separator(widget=self.unitsBox, height=3)
        self.intraSeqDelimLineEdit = gui.lineEdit(
            widget=self.unitsBox,
            master=self,
            value='intraSeqDelim',
            orientation='horizontal',
            label=u'Intra-sequence delimiter:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"If 'Sequence length' above is set to a value\n"
                u"larger than 1, the (possibly empty) string\n"
                u"specified in this field will be used as a\n"
                u"delimiter between the successive segments of\n"
                u"each sequence."
            ),
        )
        gui.separator(widget=self.unitsBox, height=3)

        # Secondary unit
        self.units2Box = self.create_widgetbox(
            box=u'Secondary units',
            orientation='vertical',
            addSpace=True,
            )

        self.coocWithUnits2Checkbox = gui.checkBox(
            widget=self.units2Box,
            master=self,
            value='coocWithUnits2',
            label=u'Use secondary units',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box to count the co-occurrences of\n"
                u"primary and secondary units."
            ),
        )
        gui.separator(widget=self.units2Box, height=3)
        iBox = gui.indentedBox(
            widget=self.units2Box,
        )
        self.unit2SegmentationCombo = gui.comboBox(
            widget=iBox,
            master=self,
            value='units2',
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation for which the co-occurrences of\n"
                u"segments will be counted with respect to primary units\n"
                u"This defines the rows of the resulting crosstab, and\n"
                u"therefore the primary units define only the columns of the\n"
                u"resulting crosstab."
            )
        )
        gui.separator(widget=iBox, height=3)
        self.unit2AnnotationCombo = gui.comboBox(
            widget=iBox,
            master=self,
            value='unit2AnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=160,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether the items of the secondary unit\n"
                u"segmentation whose co-occurrences will be counted\n"
                u"are defined by the segments' content (value 'none')\n"
                u"or by their annotation values for a specific\n"
                u"annotation key."
            ),
        )
        self.coocWithUnits2Checkbox.disables.append(iBox)
        if self.coocWithUnits2:
            iBox.setDisabled(False)
        else:
            iBox.setDisabled(True)
        gui.separator(widget=self.units2Box, height=3)

        # Context box...
        self._contextsBox = self.create_widgetbox(
            box=u'Contexts',
            orientation='vertical',
            addSpace=True,
            )

        self.modeCombo = gui.comboBox(
            widget=self._contextsBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[
                u'Sliding window',
                u'Containing segmentation'
            ],
            orientation='horizontal',
            label=u'Mode',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Context specification mode.\n\n"
                u"'Sliding window': contexts are defined as all the\n"
                u"successive, overlapping sequences of n segments\n"
                u"in the 'units' segmentation.\n\n"
                u"'Containing segmentation': contexts are defined\n"
                u"as the distinct segments occurring in a given\n"
                u"segmentation.\n"
            ),
        )
        self.slidingWindowBox = gui.widgetBox(
            widget=self._contextsBox,
            orientation='vertical'
        )
        gui.separator(widget=self.slidingWindowBox, height=3)
        self.windowSizeSpin = gui.spin(
            widget=self.slidingWindowBox,
            master=self,
            value='windowSize',
            minv=2,
            maxv=2,
            step=1,
            orientation='horizontal',
            label=u'Window size:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The length of segment sequences defining contexts."
            ),
        )
        self.containingSegmentationBox = gui.widgetBox(
            widget=self._contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        self.contextSegmentationCombo = gui.comboBox(
            widget=self.containingSegmentationBox,
            master=self,
            value='_contexts',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segment types define\n"
                u"the contexts in which co-occurrences will be counted."
            ),
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        self.contextAnnotationCombo = gui.comboBox(
            widget=self.containingSegmentationBox,
            master=self,
            value="contextAnnotationKey",
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicates whether context types are defined by\n"
                u"the content of segments in the above specified\n"
                u"segmentation (value 'none') or by their annotation\n"
                u"values for a specific annotation key."
            )
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)

        gui.rubber(self.controlArea)

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Table outputs
        textable_table, orange_table = f.result()

        # Send data 
        if len(textable_table.row_ids) == 0:
            self.infoBox.setText(u'Resulting table is empty.', 'warning')
            self.send('Textable pivot crosstab', None)
            self.send('Orange table', None)
        else:
            total = sum([i for i in textable_table.values.values()])
            message = u'Table with %i cooccurrence@p sent to output.' % total
            message = pluralize(message, total)
            self.infoBox.setText(message)
            self.send('Textable pivot crosstab', textable_table)
            self.send('Orange table', orange_table)

    def sendData(self):
        """Check input, compute co-occurrence, then send tabel"""

        # Check if there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Textable pivot crosstab', None)
            self.send('Orange table', None)
            return

        assert self.units >= 0
        # Units parameter...
        units = {
            'segmentation': self.segmentations[self.units][1],
            'annotation_key': self.unitAnnotationKey or None,
            'seq_length': self.sequenceLength,
            'intra_seq_delimiter': self.intraSeqDelim,
        }
        if units['annotation_key'] == u'(none)':
            units['annotation_key'] = None

        # Case1: sliding window
        if self.mode == 'Sliding window':

            # Partial function for threading
            threaded_function = partial(
                Processor.cooc_in_window,
                caller=self,
                units=units,
                window_size=self.windowSize,
                iterations=len(units['segmentation']) - (self.windowSize - 1),
            )

        # Case2: containing segmentation
        elif self.mode == 'Containing segmentation':
            assert self._contexts >= 0
            contexts = {
                'segmentation': self.segmentations[self._contexts][1],
                'annotation_key': self.contextAnnotationKey or None,
            }

            if contexts['annotation_key'] == u'(none)':
                contexts['annotation_key'] = None

            if self.units2 >= 0 and self.coocWithUnits2:
                # Secondary units parameter...
                units2 = {
                    'segmentation': self.segmentations[self.units2][1],
                    'annotation_key': self.unit2AnnotationKey or None,
                }
                if units2['annotation_key'] == u'(none)':
                    units2['annotation_key'] = None

                # Partial function for threading
                threaded_function = partial(
                    Processor.cooc_in_context,
                    caller=self,
                    units=units,
                    contexts=contexts,
                    units2=units2,
                    iterations=len(contexts['segmentation']) * 2,
                )
                
            else:
                # Partial function for threading
                threaded_function = partial(
                    Processor.cooc_in_context,
                    caller=self,
                    units=units,
                    contexts=contexts,
                    iterations=len(contexts['segmentation']),
                )
        
        # Infobox and progress bar
        self.infoBox.setText(u"Step 1/3: Pre-processing (count units)...", "warning")
        self.progressBarInit()
        
        # Threading ...
        self.threading(threaded_function)
        
    def inputData(self, newItem, newId=None):
        """Process incoming data."""
        # Cancel pending tasks, if any
        self.cancel()
        
        self.closeContext()
        updateMultipleInputs(
            self.segmentations,
            newItem,
            newId,
            self.onInputRemoval
        )
        self.infoBox.inputChanged()
        self.updateGUI()

    def onInputRemoval(self, index):
        """Handle removal of input with given index"""
        if index < self.units:
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations) - 1:
            self.units -= 1
        if index < self.units2:
            self.units2 -= 1
        elif index == self.units2 and self.units2 == len(
                self.segmentations) - 1:
            self.units2 -= 1
        if self.mode == u'Containing segmentation':
            if index < self._contexts:
                self._contexts -= 1
            elif index == self._contexts:
                if self._contexts == len(self.segmentations) - 1:
                    self._contexts -= 1
                if self.autoSend:
                    self.autoSend = False
                self.infoBox.setText(
                    u"The selected context segmentation has been removed.\n"
                    u"'Send automatically' checkbox will be unchecked.\n"
                    u"Please connect a segmentation to the widget and\n"
                    u"try again.",
                    state='warning',
                )
                self.send('Textable pivot crosstab', None)
                self.send('Orange table', None)

    def updateGUI(self):

        """Update GUI state"""

        self.unitsegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')
        self.unit2SegmentationCombo.clear()
        self.unit2AnnotationCombo.clear()
        self.unit2AnnotationCombo.addItem(u'(none)')

        if len(self.segmentations) == 0:
            self.units = -1
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
            self.units2 = -1
            self.unit2AnnotationKey = u''
            self.units2Box.setDisabled(True)
            self.mode = 'Sliding window'
            self._contextsBox.setDisabled(True)
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
            for segmentation in self.segmentations:
                try:
                    self.unitsegmentationCombo.addItem(segmentation[1].label)
                except TypeError:
                    self.unitsBox.setDisabled(True)
            self.units = max(self.units, 0)
            unitAnnotationKeys \
                = self.segmentations[self.units][1].get_annotation_keys()
            for k in unitAnnotationKeys:
                self.unitAnnotationCombo.addItem(k)
            if self.unitAnnotationKey not in unitAnnotationKeys:
                self.unitAnnotationKey = u'(none)'
            self.unitAnnotationKey = self.unitAnnotationKey
            self.unitsBox.setDisabled(False)
            self.sequenceLengthSpin.setRange(
                1,
                len(self.segmentations[self.units][1])
            )
            self.sequenceLength = self.sequenceLength
            if self.sequenceLength > 1:
                self.units2Box.setDisabled(True)
            else:
                self.units2Box.setDisabled(False)
            self._contextsBox.setDisabled(False)

        if self.mode == u'Sliding window':
            self.units2 = -1
            self.units2Box.setDisabled(True)
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)
            self.sequenceLengthSpin.setDisabled(False)
            self.intraSeqDelimLineEdit.setDisabled(False)

            self.windowSizeSpin.setRange(
                2,
                len(self.segmentations[self.units][1])
            )
            self.windowSize = self.windowSize

        elif self.mode == u'Containing segmentation':
            if len(self.segmentations) == 1:
                self.units2 = -1
                self.unit2AnnotationKey = u''
                self.units2Box.setDisabled(True)
            elif len(self.segmentations) >= 2:
                self.units2Box.setDisabled(False)
            self.slidingWindowBox.setVisible(False)
            self.sequenceLengthSpin.setDisabled(self.coocWithUnits2)
            self.intraSeqDelimLineEdit.setDisabled(self.coocWithUnits2)
            self.containingSegmentationBox.setVisible(True)
            self.contextSegmentationCombo.clear()
            try:
                for index in range(len(self.segmentations)):
                    self.contextSegmentationCombo.addItem(
                        self.segmentations[index][1].label
                    )
            except TypeError:
                self._contextsBox.setDisabled(True)
            self._contexts = max(self._contexts, 0)
            segmentation = self.segmentations[self._contexts]
            self.contextAnnotationCombo.clear()
            self.contextAnnotationCombo.addItem(u'(none)')
            contextAnnotationKeys = segmentation[1].get_annotation_keys()
            for key in contextAnnotationKeys:
                self.contextAnnotationCombo.addItem(key)
            if self.contextAnnotationKey not in contextAnnotationKeys:
                self.contextAnnotationKey = u'(none)'
            self.contextAnnotationKey = self.contextAnnotationKey
            if self.coocWithUnits2:
                try:
                    for segmentation in self.segmentations:
                        self.unit2SegmentationCombo.addItem(
                            segmentation[1].label)
                except TypeError:
                    self.units2Box.setDisabled(True)
                self.units2 = max(self.units2, 0)
                unit2AnnotationKeys \
                    = self.segmentations[self.units2][1].get_annotation_keys()
                for k in unit2AnnotationKeys:
                    self.unit2AnnotationCombo.addItem(k)
                if self.unit2AnnotationKey not in unit2AnnotationKeys:
                    self.unit2AnnotationKey = u'(none)'
                self.unit2AnnotationKey = self.unit2AnnotationKey
                self.sequenceLength = 1

    def handleNewSignals(self):
        """Overridden: called after multiple singnals have been added"""
        self.openContext(self.uuid, self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    import LTTL.Segmenter as Segmenter
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableCooccurrence()
    seg1 = Input(u'un texte', label=u'text')
    seg2 = Segmenter.tokenize(
        seg1,
        regexes=[
            (
                re.compile(r'\w+'),
                u'tokenize',
                {'type': 'W'},
            )
        ],
        label=u'words',
    )
    seg3 = Segmenter.tokenize(
        seg1,
        regexes=[
            (
                re.compile(r'[aeiouy]'),
                u'tokenize',
                {'type': 'V'},
            )
        ],
        label=u'vowel',
    )
    seg4 = Segmenter.tokenize(
        seg1,
        regexes=[
            (
                re.compile(r'[^aeiouy]'),
                u'tokenize',
                {'type2': 'C'},
            )
        ],
        label=u'consonant',
    )
    ow.inputData(seg3, 1)
    ow.inputData(seg2, 2)
    ow.inputData(seg4, 3)

    ow.show()
    appl.exec_()
    ow.saveSettings()
