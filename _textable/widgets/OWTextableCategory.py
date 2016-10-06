"""
Class OWTextableCategory
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
"""

__version__ = '0.12.3'

from LTTL.Table import Table
from LTTL.Segmentation import Segmentation
import LTTL.Processor as Processor

from .TextableUtils import (
    OWTextableBaseWidget,
    InfoBox, SendButton, updateMultipleInputs, SegmentationListContextHandler,
    SegmentationsInputList
)
import Orange.data
from Orange.widgets import widget, gui, settings


class OWTextableCategory(OWTextableBaseWidget):
    """Orange widget for extracting content or annotation information"""

    name = "Category"
    description = "Build a table with categories defined by segments' " \
                  "content or annotations."
    icon = "icons/Category.png"
    priority = 8006

    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [('Textable table', Table, widget.Default),
               ('Orange table', Orange.data.Table)]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.split(".")[:2]
    )
    segmentations = SegmentationsInputList()  # type: list

    intraSeqDelim = settings.Setting(u'#')
    sortOrder = settings.Setting(u'Frequency')
    sortReverse = settings.Setting(True)
    keepOnlyFirst = settings.Setting(True)
    valueDelimiter = settings.Setting(u'|')

    units = settings.ContextSetting(-1)
    _contexts = settings.ContextSetting(-1)
    unitAnnotationKey = settings.ContextSetting(-1)
    contextAnnotationKey = settings.ContextSetting(-1)
    sequenceLength = settings.ContextSetting(1)

    want_main_area = False

    def __init__(self):

        """Initialize a Category widget"""

        super().__init__()

        self.infoBox = InfoBox(
            widget=self.controlArea,
            stringClickSend=u", please click 'Send' when ready.",
        )
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            infoBoxAttribute='infoBox',
            buttonLabel=u'Send',
            checkboxLabel=u'Send automatically',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Units box
        self.unitsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Units',
            orientation='vertical',
            addSpace=True,
        )
        self.unitSegmentationCombo = gui.comboBox(
            widget=self.unitsBox,
            master=self,
            value='units',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segments will be used for\n"
                u"determining categories."
            ),
        )
        self.unitSegmentationCombo.setMinimumWidth(120)
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
                u"Indicate whether categories are defined by the\n"
                u"segments' content (value 'none') or by their\n"
                u"annotation values for a specific annotation key."
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
                u"Indicate whether to use single segments or rather\n"
                u"sequences of 2, 3, ... segments (n-grams) for\n"
                u"category extraction."
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

        # Multiple Values box
        self.multipleValuesBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Multiple Values',
            orientation='vertical',
            addSpace=True,
        )
        self.sortOrderCombo = gui.comboBox(
            widget=self.multipleValuesBox,
            master=self,
            value='sortOrder',
            items=[u'Frequency', u'ASCII'],
            sendSelectedValue=True,
            orientation='horizontal',
            label=u'Sort by:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Criterion for sorting multiple categories."
            ),
        )
        self.sortOrderCombo.setMinimumWidth(120)
        gui.separator(widget=self.multipleValuesBox, height=3)
        self.sortReverseCheckBox = gui.checkBox(
            widget=self.multipleValuesBox,
            master=self,
            value='sortReverse',
            label=u'Sort in reverse order',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Sort in reverse (i.e. decreasing) order."
            ),
        )
        gui.separator(widget=self.multipleValuesBox, height=3)
        gui.checkBox(
            widget=self.multipleValuesBox,
            master=self,
            value='keepOnlyFirst',
            label=u'Keep only first value',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Keep only the first category\n"
                u"(after sorting)."
            ),
        )
        gui.separator(widget=self.multipleValuesBox, height=3)
        self.multipleValuesDelimLineEdit = gui.lineEdit(
            widget=self.multipleValuesBox,
            master=self,
            value='valueDelimiter',
            orientation='horizontal',
            label=u'Value delimiter:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"If 'Keep only first value' above is unchecked\n"
                u"and there are multiple categories, the (possibly\n"
                u"empty) string specified in this field will be\n"
                u"used as a delimiter between them."
            ),
        )
        gui.separator(widget=self.multipleValuesBox, height=3)

        # Contexts box...
        self.contextsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Contexts',
            orientation='vertical',
            addSpace=True,
        )
        self.contextSegmentationCombo = gui.comboBox(
            widget=self.contextsBox,
            master=self,
            value='_contexts',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segment types define\n"
                u"the contexts to which categories will be\n"
                u"assigned."
            ),
        )
        gui.separator(widget=self.contextsBox, height=3)
        self.contextAnnotationCombo = gui.comboBox(
            widget=self.contextsBox,
            master=self,
            value='contextAnnotationKey',
            sendSelectedValue=True,
            emptyString=u'(none)',
            orientation='horizontal',
            label=u'Annotation key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Indicate whether context types are defined by\n"
                u"the content of segments in the above specified\n"
                u"segmentation (value 'none') or by their\n"
                u"annotation values for a specific annotation key."
            ),
        )
        gui.separator(widget=self.contextsBox, height=3)

        gui.rubber(self.controlArea)

        # Send button...
        self.sendButton.draw()

        # Info box...
        self.infoBox.draw()

        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

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
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations) - 1:
            self.units -= 1
            if self.units < 0:
                self.units = None
        if index == self._contexts:
            self.mode = u'No context'
            self._contexts = None
        elif index < self._contexts:
            self._contexts -= 1
            if self._contexts < 0:
                self.mode = u'No context'
                self._contexts = None

    def sendData(self):

        """Check input, build table, then send it"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Textable table', None)
            self.send('Orange table', None)
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

        # Multiple values parameter...
        multipleValues = {
            'sort_order': self.sortOrder,
            'reverse': self.sortReverse,
            'keep_only_first': self.keepOnlyFirst,
            'value_delimiter': self.valueDelimiter,
        }

        # Contexts parameter...
        contexts = {
            'segmentation': self.segmentations[self._contexts][1],
            'annotation_key': self.contextAnnotationKey or None,
        }
        if contexts['annotation_key'] == u'(none)':
            contexts['annotation_key'] = None

        # Count...
        progressBar = gui.ProgressBar(
            self,
            iterations=len(contexts['segmentation'])
        )
        table = Processor.annotate_contexts(
            units,
            multipleValues,
            contexts,
            progress_callback=progressBar.advance,
        )
        progressBar.finish()

        if not len(table.row_ids):
            self.infoBox.setText(u'Resulting table is empty.', 'warning')
            self.send('Textable table', None)
            self.send('Orange table', None)
        else:
            self.infoBox.setText(u'Table sent to output.')
            self.send('Textable table', table)
            self.send('Orange table', table.to_orange_table())

        self.sendButton.resetSettingsChangedFlag()

    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')

        if len(self.segmentations) == 0:
            self.units = None
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
            self.contextsBox.setDisabled(True)
            self.adjustSize()
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
            for segmentation in self.segmentations:
                self.unitSegmentationCombo.addItem(segmentation[1].label)
            self.units = self.units
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
            self.sequenceLength = self.sequenceLength or 1
            self.contextsBox.setDisabled(False)
            self.contextSegmentationCombo.clear()
            for index in range(len(self.segmentations)):
                self.contextSegmentationCombo.addItem(
                    self.segmentations[index][1].label
                )
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

        self.adjustSizeWithTimer()

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext(self.uuid, self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()


if __name__ == '__main__':
    import sys
    import re
    from PyQt4.QtGui import  QApplication
    from LTTL.Input import Input
    from LTTL import Segmenter as segmenter

    appl = QApplication(sys.argv)
    ow = OWTextableCategory()
    seg1 = Input(u'aaabc', 'text1')
    seg2 = Input(u'abbc', 'text2')
    # segmenter = Segmenter()
    seg3 = segmenter.concatenate(
        [seg1, seg2],
        import_labels_as='string',
        label='corpus'
    )
    seg4 = segmenter.tokenize(
        seg3,
        regexes=[(re.compile(r'\w+'), u'tokenize',)],
    )
    seg5 = segmenter.tokenize(
        seg4,
        regexes=[(re.compile(r'[ai]'), u'tokenize',)],
        label='V'
    )
    seg6 = segmenter.tokenize(
        seg4,
        regexes=[(re.compile(r'[bc]'), u'tokenize',)],
        label='C'
    )
    seg7 = segmenter.concatenate(
        [seg5, seg6],
        import_labels_as='category',
        label='letters',
        sort=True,
        merge_duplicates=True,
    )
    ow.inputData(seg7, 1)
    ow.inputData(seg4, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
