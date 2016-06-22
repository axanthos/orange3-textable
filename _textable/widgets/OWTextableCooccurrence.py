# -*- coding: cp1252 -*-
"""
Class OWTextableCooccurrence
Copyright 2016 University of Lausanne
-----------------------------------------------------------------------------
This file is part of the Orange-Textable-Prototypes package v0.1.

Orange-Textable-Prototypes v0.1 is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange-Textable-Prototypes v0.1 is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange-Textable-Prototypes v0.1. If not, see
<http://www.gnu.org/licenses/>.
"""

__version__ = u'0.1.1'
__author__ = "Mahtab Mohammadi"
__maintainer__ = "Aris Xanthos"
__email__ = "aris.xanthos@unil.ch"

"""
<name>Cooccurrence</name>
<description>Measure segment types' co-occurrence</description>
<icon>icons/Cooccurrence.png</icon>
<priority>12</priority>
"""

import numpy as np
from _textable.widgets.LTTL.Table import IntPivotCrosstab, PivotCrosstab
from _textable.widgets.LTTL.Processor import Processor
from _textable.widgets.LTTL.Segmentation import Segmentation

from _textable.widgets.TextableUtils import *

import Orange
from Orange.OrangeWidgets.OWWidget import *
import OWGUI

import re

class OWTextableCooccurrence(OWWidget):

    """Orange widget for calculating co-occurrences of text units"""

    contextHandlers = {
        '': SegmentationListContextHandler(
            '', [
                ContextInputListField('segmentations'),
                ContextInputIndex('units'),
                ContextInputIndex('_contexts'),
                ContextInputIndex('units2'),
                'mode',
                'unitAnnotationKey',
                'unit2AnnotationKey',
                'contextAnnotationKey',
                'coocWithUnits2'
                'sequenceLength',
                'windowSize',
                'uuid',
            ]
        )
    }

    settingsList = [
        'autoSend',
        'intraSeqDelim',
        'sequenceLength',
        'windowSize',
        'coocWithUnits2'
    ]

    def __init__(self, parent=None, signalManager=None):

        """Initialize a Co-oc widget"""

        OWWidget.__init__(
            self,
            parent,
            signalManager,
            wantMainArea=0,
        )

        self.inputs  = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs =  [('Pivot Crosstab', IntPivotCrosstab)]

        #Settings...
        self.autoSend = False
        self.sequenceLength = 1
        self.intraSeqDelim = u'#'
        self.mode = u'Sliding window'
        self.coocWithUnits2 = False
        self.windowSize = 2
        self.units = None
        self.unitAnnotationKey = None
        self.units2 = None
        self.unit2AnnotationKey = None
        self._contexts = None
        self.contextAnnotationKey = None
        self.uuid = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)


        #Other attributes...
        self.processor = Processor()
        self.segmentations = list()
        self.infoBox = InfoBox(
            widget = self.controlArea,
            stringClickSend = u", please click 'Compute' when ready.",
        )
        self.sendButton = SendButton(
            widget = self.controlArea,
            master = self,
            callback = self.sendData,
            infoBoxAttribute = 'infoBox',
            buttonLabel = u'Compute',
            checkboxLabel       = u'Compute automatically',
            sendIfPreCallback = self.updateGUI,
        )


        #GUI...

        #Units box
        self.unitsBox = OWGUI.widgetBox(
            widget = self.controlArea,
            box = u'Units',
            orientation = 'vertical',
            addSpace = True,
        )
        self.unitsegmentationCombo = OWGUI.comboBox(
            widget = self.unitsBox,
            master = self,
            value = 'units',
            orientation = 'horizontal',
            label = u'Segmentation:',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"The segmentation for which the co-occurrence of the\n"
                u"segments will be measured.\n"
                u"This defines the columns and rows of the resulting\n"
                u"crosstab."
            ),
        )
        self.unitsegmentationCombo.setMinimumWidth(120)
        OWGUI.separator(
            widget = self.unitsBox,
            height = 3,
        )
        self.unitAnnotationCombo = OWGUI.comboBox(
            widget = self.unitsBox,
            master = self,
            value = 'unitAnnotationKey',
            sendSelectedValue = True,
            emptyString = u'(none)',
            orientation = 'horizontal',
            label = u'Annotation key:',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Indicate wether the items to be measured the\n"
                u"cooccurrence in the above specified segmentation\n"
                u"are defined by the segments' content (value 'none')\n"
                u"or by their annotation values for a specific\n"
                u"annotation key."
            ),
        )
        OWGUI.separator(
            widget = self.unitsBox,
            height = 3,
        )
        self.sequenceLengthSpin = OWGUI.spin(
            widget = self.unitsBox,
               master = self,
            value = 'sequenceLength',
            min = 1,
            max = 1,
            step = 1,
            orientation = 'horizontal',
            label = u'Sequence length:',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Indicates whether to measure the co-occurrence of\n"
                u"single segments or rather of sequences of 2,\n"
                u"3,... segments (n-grams).\n\n"
                u"Note that this parameter cannot be set to a\n"
                u"value larger than 1 if co-occurrence is to be\n"
                u"measured with respect to the secondary units."
            ),
        )
        OWGUI.separator(
            widget = self.unitsBox,
            height = 3,
        )
        self.intraSeqDelimLineEdit = OWGUI.lineEdit(
            widget = self.unitsBox,
            master          = self,
            value           = 'intraSeqDelim',
            orientation     = 'horizontal',
            label           = u'Intra-sequence delimiter:',
            labelWidth      = 180,
            callback        = self.sendButton.settingsChanged,
            tooltip         = (
                u"If 'Sequence length' above is set to a value\n"
                u"larger than 1, the (possibly empty) string\n"
                u"specified in this field will be used as a\n"
                u"delimiter between the successive segments of\n"
                u"each sequence."
            ),
        )
        OWGUI.separator(
            widget = self.unitsBox,
            height = 3,
        )

        #Secondary unit
        self.units2Box = OWGUI.widgetBox(
            widget = self.controlArea,
            box = u'Secondary units',
            orientation = 'vertical',
            addSpace = True,
        )
        self.coocWithUnits2Checkbox = OWGUI.checkBox(
            widget = self.units2Box,
            master = self,
            value = 'coocWithUnits2',
            label = u'Use secondary units',
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Check this box to measure the co-occurrence of\n"
                u"the primary and the secondary units."
            ),
        )
        OWGUI.separator(
            widget = self.units2Box,
            height = 3,
        )
        iBox = OWGUI.indentedBox(
            widget = self.units2Box,
        )
        self.unit2SegmentationCombo = OWGUI.comboBox(
            widget = iBox,
            master = self,
            value = 'units2',
            emptyString = u'(none)',
            orientation = 'horizontal',
            label = u'Segmentation:',
            labelWidth = 160,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"The segmentation for which the co-occurrence of the\n"
                u"segments will be measured with respect to primary units\n"
                u"This defines the rows of the resulting crosstab, and\n"
                u"therefor the primary units define only the columns of the\n"
                u"resulting crosstab."
            )
        )
        OWGUI.separator(
            widget = iBox,
            height = 3,
        )
        self.unit2AnnotationCombo = OWGUI.comboBox(
            widget = iBox,
            master = self,
            value = 'unit2AnnotationKey',
            sendSelectedValue = True,
            emptyString = u'(none)',
            orientation = 'horizontal',
            label = u'Annotation key:',
            labelWidth = 160,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Sepecify the annotation values of the secondary units n"
                u"for a specific annotation key."
            ),
        )
        self.coocWithUnits2Checkbox.disables.append(iBox)
        if self.coocWithUnits2:
            iBox.setDisabled(False)
        else:
            iBox.setDisabled(True)
        OWGUI.separator(
            widget = self.units2Box,
            height = 3,
        )

        #Context box...
        self._contextsBox = OWGUI.widgetBox(
            widget = self.controlArea,
            box = u'Contexts',
            orientation = 'vertical',
            addSpace = True,
        )
        self.modeCombo = OWGUI.comboBox(
            widget = self._contextsBox,
            master = self,
            value = 'mode',
            sendSelectedValue = True,
            items = [
                u'Sliding window',
                u'Containing segmentation'
            ],
            orientation = 'horizontal',
            label = u'Mode',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Context specification mode.\n\n"
                u"'Sliding window': contexts are defined as all the\n"
                u"successive, overlaping sequences of n segments\n"
                u"in the 'units' segmentation.\n\n"
                u"'Containing segmentation': contexts are defined\n"
                u"as the distinct segments occurring in a given\n"
                u"segmentation.\n"
            ),
        )
        self.slidingWindowBox = OWGUI.widgetBox(
            widget = self._contextsBox,
            orientation = 'vertical'
        )
        OWGUI.separator(
            widget = self.slidingWindowBox,
            height = 3,
        )
        self.windowSizeSpin = OWGUI.spin(
            widget = self.slidingWindowBox,
            master = self,
            value = 'windowSize',
            min = 2,
            max = 2,
            step = 1,
            orientation = 'horizontal',
            label = u'Window size:',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"The length of segment sequences defining contexts."
            ),
        )
        self.containingSegmentationBox = OWGUI.widgetBox(
            widget = self._contextsBox,
            orientation = 'vertical',
        )
        OWGUI.separator(
            widget = self.containingSegmentationBox,
            height = 3,
        )
        self.contextSegmentationCombo = OWGUI.comboBox(
            widget = self.containingSegmentationBox,
            master = self,
            value = '_contexts',
            orientation = 'horizontal',
            label = u'Segmentation:',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"The segmentation whose segment types define\n"
                u"the contexts in which the co-occurrence of the \n"
                u"unit types segmentation will be measured."
            ),
        )
        OWGUI.separator(
            widget = self.containingSegmentationBox,
            height = 3,
        )
        self.contextAnnotationCombo = OWGUI.comboBox(
            widget = self.containingSegmentationBox,
            master = self,
            value = "contextAnnotationKey",
            sendSelectedValue = True,
            emptyString = u'(none)',
            orientation = 'horizontal',
            label = u'Annotation key:',
            labelWidth = 180,
            callback = self.sendButton.settingsChanged,
            tooltip = (
                u"Indicate whether context types are defines by\n"
                u"the content of segments in the above specified\n"
                u"segmentation (value 'none') or by their annotation\n"
                u"values for a specific annotation key."
            )
        )
        OWGUI.separator(
            widget = self.containingSegmentationBox,
            height = 3,
        )


        # Info box...
        self.infoBox.draw()

        # Send button...
        self.sendButton.draw()
        self.sendButton.sendIf()


    def inputData(self, newItem, newId=None):
        """Process incoming data."""
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
            self.units = self.units - 1
        elif index == self.units and self.units == len(self.segmentations)-1:
            self.units = self.units - 1
            if self.units <0:
                self.units = None
        if index < self.units2:
            self.units2 = self.units2 - 1
        elif index == self.units2 and self.units2 == len(self.segmentations)-1:
            self.units2 = self.units2 - 1
            if self.units2 < 0:
                self.units2 = None
        if self.mode == u'Containing segmentation':
            if index < self._contexts:
                self._contexts = self._contexts - 1
            elif index == self._contexts:
                if self._contexts == len(self.segmentations)-1:
                    self._contexts = self._contexts - 1
                    if self._contexts < 0:
                        self._contexts = None
                if self.autoSend:
                    self.autoSend = False
                self.infoBox.noDataSent(
                    warning=
                    u"The selected context segmentation has been removed.\n"
                    u"The automatic computation box will be unchecked in\n"
                    u"case it was checked. Please connect a segmentation\n"
                    u"to the widget and try again."

                )
                self.send('IntPivotCrosstab', None, self)


    def sendData(self):
        """Check input, compute co-occurrence, then send tabel"""

        # Check if there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.noDataSent(u'No input segmentation.')
            self.send('Pivot Crosstab', None)
            return

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
            progressBar = OWGUI.ProgressBar(
                self,
                iterations = len(units['segmentation'])
                    -(self.windowSize - 1)
            )
            # Calculate the co-occurrence...
            table = cooc_in_window(
                units,
                window_size = self.windowSize,
                   progress_callback = progressBar.advance,
            )
            progressBar.finish()

        # Case2: containing segmentation
        elif self.mode == 'Containing segmentation':
                contexts = {
                    'segmentation': self.segmentations[self._contexts][1],
                    'annotation_key': self.contextAnnotationKey or None,
                }
                if contexts['annotation_key'] == u'(none)':
                    contexts['annotation_key'] = None
                if self.units2 != None and self.coocWithUnits2:
                    # Secondary units parameter...
                    units2 = {
                        'segmentation': self.segmentations[self.units2][1],
                        'annotation_key': self.unit2AnnotationKey or None,
                    }
                    if units2['annotation_key'] == u'(none)':
                        units2['annotation_key'] = None
                    num_iterations = len(contexts['segmentation'])
                    progressBar = OWGUI.ProgressBar(
                        self,
                        iterations = num_iterations*2
                    )                    
                    # Calculate the co-occurrence with secondary units...
                    table = cooc_in_context(
                        units,
                        contexts,
                        units2,
                        progress_callback = progressBar.advance,
                    )
                else:
                    num_iterations = (len(contexts['segmentation']))
                    progressBar = OWGUI.ProgressBar(
                        self,
                        iterations = num_iterations
                    )
                    # Calculate the co-occurrence without secondary units...
                    table = cooc_in_context(
                        units,
                        contexts,
                        progress_callback = progressBar.advance,
                    )
                progressBar.finish()
        if not len(table.row_ids):
            self.infoBox.noDataSent(warning = u'Resulting table is empty.')
            self.send('Pivot Crosstab', None)
        else:
            self.send('Pivot Crosstab', table)
            self.infoBox.dataSent()

        self.sendButton.resetSettingsChangedFlag()

    def updateGUI(self):

        """Update GUI state"""

        self.unitsegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')
        self.unit2SegmentationCombo.clear()
        self.unit2AnnotationCombo.clear()
        self.unit2AnnotationCombo.addItem(u'(none)')

        if len(self.segmentations) == 0:
            self.units = None
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
            self.units2 = None
            self.unit2AnnotationKey = u''
            self.units2Box.setDisabled(True)
            self.mode = 'Sliding window'
            self._contextsBox.setDisabled(True)
            self.adjustSize()
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
            for segmentation in self.segmentations:
                try:
                    self.unitsegmentationCombo.addItem(segmentation[1].label)
                except TypeError:
                    self.unitsBox.setDisabled(True)
            self.units = self.units
            unitAnnotationKeys \
                = self.segmentations[self.units][1].get_annotation_keys()
            for k in unitAnnotationKeys:
                self.unitAnnotationCombo.addItem(k)
            if self.unitAnnotationKey not in unitAnnotationKeys:
                self.unitAnnotationKey = u'(none)'
            self.unitAnnotationKey = self.unitAnnotationKey
            self.unitsBox.setDisabled(False)
            self.sequenceLengthSpin.control.setRange(
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
            self.units2 = None
            self.units2Box.setDisabled(True)
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)
            self.sequenceLengthSpin.setDisabled(False)

            self.windowSizeSpin.control.setRange(
                2,
                len(self.segmentations[self.units][1])
            )
            self.windowSize = self.windowSize

        elif self.mode == u'Containing segmentation':
            if len(self.segmentations) == 1:
                self.units2 = None
                self.unit2AnnotationKey = u''
                self.units2Box.setDisabled(True)
            elif len(self.segmentations) >= 2:
                self.units2Box.setDisabled(False)
            self.slidingWindowBox.setVisible(False)
            self.containingSegmentationBox.setVisible(True)
            self.contextSegmentationCombo.clear()
            try:
                for index in range(len(self.segmentations)):
                    self.contextSegmentationCombo.addItem(
                        self.segmentations[index][1].label
                    )
            except TypeError:
                self._contextsBox.setDisabled(True)
            self._contexts = self._contexts or 0
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
                        self.unit2SegmentationCombo.addItem(segmentation[1].label)
                except TypeError:
                    self.units2Box.setDisabled(True)
                self.units2 = self.units2 or 0
                unit2AnnotationKeys \
                    = self.segmentations[self.units2][1].get_annotation_keys()
                for k in unit2AnnotationKeys:
                    self.unit2AnnotationCombo.addItem(k)
                if self.unit2AnnotationKey not in unit2AnnotationKeys:
                    self.unit2AnnotationKey = u'(none)'
                self.unit2AnnotationKey = self.unit2AnnotationKey
                self.sequenceLength = 1
                self.sequenceLengthSpin.setDisabled(True)

        self.adjustSize()

    def handleNewSignals(self):

        """Overridden: called after multiple singnals have been added"""
        self.openContext("",self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()


    def getSettings(self, *args, **kwargs):
        settings = OWWidget.getSettings(self, *args, **kwargs)
        settings["settingsDataVersion"] = __version__.split('.')[:2]
        return settings

    def setSettings(self, settings):
        if settings.get("settingsDataVersion", None) \
            == __version__.split('.')[:2]:
            settings = settings.copy()
            del settings["settingsDataVersion"]
            OWWidget.setSettings(self, settings)


def cooc_in_window(
    units=None,
    window_size=2,
    progress_callback=None,
):
    """ Measure the cooccurrence in sliding window """
    processor = Processor()
    contingency = processor.count_in_window(
    units,
    window_size,
    progress_callback,
    )
    normalized = contingency.to_normalized('presence/absence')
    np_contingency = normalized.to_numpy()
    cooc = np.dot(
    np.transpose(np_contingency),
    np_contingency,
    )
    return IntPivotCrosstab.from_numpy(
    contingency.col_ids[:],
    contingency.col_ids[:],
    cooc,
    contingency.header_row.copy(),
    contingency.header_row.copy(),
    contingency.col_type,
    )


def cooc_in_context(
    units=None,
    contexts= None,units2=None,
    progress_callback=None,
):
    """ Measure the cooccurrence in a context type segmentation"""
    processor = Processor()
    contingency = processor.count_in_context(
    units,
    contexts,
    progress_callback,
    )
    normalized = contingency.to_normalized('presence/absence')
    np_contingency = normalized.to_numpy()
    if units2 is not None:
        contingency2 = processor.count_in_context(
            units2,
            contexts,
            progress_callback,
        )
        normalized2 = contingency2.to_normalized('presence/absence')
        np_contingency2 = normalized2.to_numpy()
        row_labels = contingency.row_ids
        row_labels2 = contingency2.row_ids
        keep_from_contingency = [
            i for i in xrange(len(row_labels)) if row_labels[i] in row_labels2
        ]
        keep_from_contingency2 =[
            i for i in xrange(len(row_labels2)) if row_labels2[i] in row_labels
        ]
        try:
            np_contingency = np_contingency[keep_from_contingency].astype(int)
            np_contingency2 = np_contingency2[keep_from_contingency2].astype(int)
            cooc = np.dot(np.transpose(np_contingency2), np_contingency)
            return IntPivotCrosstab.from_numpy(
                contingency2.col_ids[:],
                contingency.col_ids[:],
                cooc,
                contingency.header_col.copy(),
                contingency2.header_col.copy(),
                contingency.col_type,
            )   
        except IndexError:
            return IntPivotCrosstab(None)
    else:
        cooc = np.dot(np.transpose(np_contingency), np_contingency)
        return IntPivotCrosstab.from_numpy(
            contingency.col_ids[:],
            contingency.col_ids[:],
            cooc,
            contingency.header_col.copy(),
            contingency.header_col.copy(),
            contingency.col_type,
        )


if __name__ == '__main__':
    from _textable.widgets.LTTL.Segmenter import Segmenter
    from _textable.widgets.LTTL.Input import Input
    appl = QApplication(sys.argv)
    ow = OWTextableCooccurrence()
    seg1 = Input(u'un texte', label=u'text')
    segmenter = Segmenter()
    seg2 = segmenter.tokenize(
        seg1,
        regexes = [
            (
                re.compile(r'\w+'),
                u'Tokenize',
                {'type': 'W'},
            )
        ],
        label = u'words',
    )
    seg3 = segmenter.tokenize(
        seg1,
        regexes = [
            (
                re.compile(r'[aeiouy]'),
                u'Tokenize',
                {'type':'V'},
            )
        ],
        label = u'vowel',
    )
    seg4 = segmenter.tokenize(
        seg1,
        regexes = [
            (
                re.compile(r'[^aeiouy]'),
                u'Tokenize',
                {'type2':'C'},
            )
        ],
        label = u'consonant',
    )
    ow.inputData(seg3, 1)
    ow.inputData(seg2, 2)
    ow.inputData(seg4, 3)

    ow.show()
    appl.exec_()
    ow.saveSettings()
