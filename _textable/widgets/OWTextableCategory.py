#=============================================================================
# Class OWTextableCategory
# Copyright 2012-2015 LangTech Sarl (info@langtech.ch)
#=============================================================================
# This file is part of the Textable (v1.5) extension to Orange Canvas.
#
# Textable v1.5 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Textable v1.5 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Textable v1.5. If not, see <http://www.gnu.org/licenses/>.
#=============================================================================

__version__ = '0.12.1'

"""
<name>Category</name>
<description>Build a table with categories defined by segments' content or
annotations.</description>
<icon>icons/Category.png</icon>
<priority>8004</priority>
"""

from LTTL.Table        import Table
from LTTL.Processor    import Processor
from LTTL.Segmentation import Segmentation

from TextableUtils      import *

import Orange
from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableCategory(OWWidget):

    """Orange widget for extracting content or annotation information"""

    contextHandlers = {
        '': SegmentationListContextHandler(
            '', [
                ContextInputListField('segmentations'),
                ContextInputIndex('units'),
                ContextInputIndex('contexts'),
                'unitAnnotationKey',
                'contextAnnotationKey',
                'sequenceLength',
                'uuid',
            ]
        )
    }

    settingsList = [
            'autoSend',
            'intraSeqDelim',
            'sortOrder',
            'sortReverse',
            'keepOnlyFirst',
            'valueDelimiter',
            'sequenceLength',
    ]

    def __init__(self, parent=None, signalManager=None):
        
        """Initialize a Category widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )
        
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [('Textable table', Table)]
        
        # Settings...
        self.autoSend               = False
        self.sequenceLength         = 1
        self.intraSeqDelim          = u'#'
        self.sortOrder              = u'Frequency'
        self.sortReverse            = True
        self.keepOnlyFirst          = True
        self.valueDelimiter         = u'|'
        self.uuid                   = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)

        # Other attributes...
        self.processor              = Processor()
        self.segmentations          = []
        self.units                  = None
        self.unitAnnotationKey      = None
        self.contexts               = None
        self.contextAnnotationKey   = None
        self.settingsRestored       = False                                         
        self.infoBox                = InfoBox(
                widget          = self.controlArea,
                stringClickSend = u", please click 'Compute' when ready.",
        )
        self.sendButton             = SendButton(
                widget              = self.controlArea,
                master              = self,
                callback            = self.sendData,
                infoBoxAttribute    = 'infoBox',
                buttonLabel         = u'Compute',
                checkboxLabel       = u'Compute automatically',
                sendIfPreCallback   = self.updateGUI,
        )

        # GUI...

        # Units box
        self.unitsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Units',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.unitSegmentationCombo = OWGUI.comboBox(
                widget              = self.unitsBox,
                master              = self,
                value               = 'units',
                orientation         = 'horizontal',
                label               = u'Segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose segments will be used for\n"
                        u"determining categories."
                ),
        )
        self.unitSegmentationCombo.setMinimumWidth(120)
        OWGUI.separator(
                widget              = self.unitsBox,
                height              = 3,
        )
        self.unitAnnotationCombo = OWGUI.comboBox(
                widget              = self.unitsBox,
                master              = self,
                value               = 'unitAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether categories are defined by the\n"
                        u"segments' content (value 'none') or by their\n"
                        u"annotation values for a specific annotation key."
                ),
        )
        OWGUI.separator(
                widget              = self.unitsBox,
                height              = 3,
        )
        self.sequenceLengthSpin = OWGUI.spin(
                widget              = self.unitsBox,
                master              = self,
                value               = 'sequenceLength',
                min                 = 1,
                max                 = 1,
                step                = 1,
                orientation         = 'horizontal',
                label               = u'Sequence length:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether to use single segments or rather\n"
                        u"sequences of 2, 3, ... segments (n-grams) for\n"
                        u"category extraction."
                ),
        )
        OWGUI.separator(
                widget              = self.unitsBox,
                height              = 3,
        )
        self.intraSeqDelimLineEdit = OWGUI.lineEdit(
                widget              = self.unitsBox,
                master              = self,
                value               = 'intraSeqDelim',
                orientation         = 'horizontal',
                label               = u'Intra-sequence delimiter:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"If 'Sequence length' above is set to a value\n"
                        u"larger than 1, the (possibly empty) string\n"
                        u"specified in this field will be used as a\n"
                        u"delimiter between the successive segments of\n"
                        u"each sequence."
                ),
        )
        OWGUI.separator(
                widget              = self.unitsBox,
                height              = 3,
        )

        # Multiple Values box
        self.multipleValuesBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Multiple Values',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.sortOrderCombo = OWGUI.comboBox(
                widget              = self.multipleValuesBox,
                master              = self,
                value               = 'sortOrder',
                items               = [u'Frequency', u'ASCII'],
                sendSelectedValue   = True,
                orientation         = 'horizontal',
                label               = u'Sort by:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Criterion for sorting multiple categories."
                ),
        )
        self.sortOrderCombo.setMinimumWidth(120)
        OWGUI.separator(
                widget              = self.multipleValuesBox,
                height              = 3,
        )
        self.sortReverseCheckBox = OWGUI.checkBox(
                widget              = self.multipleValuesBox,
                master              = self,
                value               = 'sortReverse',
                label               = u'Sort in reverse order',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Sort in reverse (i.e. decreasing) order."
                ),
        )
        OWGUI.separator(
                widget              = self.multipleValuesBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = self.multipleValuesBox,
                master              = self,
                value               = 'keepOnlyFirst',
                label               = u'Keep only first value',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Keep only the first category\n"
                        u"(after sorting)."
                ),
        )
        OWGUI.separator(
                widget              = self.multipleValuesBox,
                height              = 3,
        )
        self.multipleValuesDelimLineEdit = OWGUI.lineEdit(
                widget              = self.multipleValuesBox,
                master              = self,
                value               = 'valueDelimiter',
                orientation         = 'horizontal',
                label               = u'Value delimiter:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"If 'Keep only first value' above is unchecked\n"
                        u"and there are multiple categories, the (possibly\n"
                        u"empty) string specified in this field will be\n"
                        u"used as a delimiter between them."
                ),
        )
        OWGUI.separator(
                widget              = self.multipleValuesBox,
                height              = 3,
        )

        # Contexts box...
        self.contextsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Contexts',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.contextSegmentationCombo = OWGUI.comboBox(
                widget              = self.contextsBox,
                master              = self,
                value               = 'contexts',
                orientation         = 'horizontal',
                label               = u'Segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose segment types define\n"
                        u"the contexts to which categories will be\n"
                        u"assigned."
                ),
        )
        OWGUI.separator(
                widget              = self.contextsBox,
                height              = 3,
        )
        self.contextAnnotationCombo = OWGUI.comboBox(
                widget              = self.contextsBox,
                master              = self,
                value               = 'contextAnnotationKey',
                sendSelectedValue   = True,
                emptyString         = u'(none)',
                orientation         = 'horizontal',
                label               = u'Annotation key:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Indicate whether context types are defined by\n"
                        u"the content of segments in the above specified\n"
                        u"segmentation (value 'none') or by their\n"
                        u"annotation values for a specific annotation key."
                ),
        )
        OWGUI.separator(
                widget              = self.contextsBox,
                height              = 3,
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
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations)-1:
            self.units -= 1
            if self.units < 0:
                self.units = None
        if index == self.contexts:
            self.mode       = u'No context'
            self.contexts   = None
        elif index < self.contexts:
            self.contexts -= 1
            if self.contexts < 0:
                self.mode     = u'No context'
                self.contexts = None


    def sendData(self):

        """Check input, build table, then send it"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.noDataSent(u': no input segmentation.')
            self.send('Textable table', None)
            return

        # Units parameter...
        units = {
                'segmentation':         self.segmentations[self.units][1],
                'annotation_key':       self.unitAnnotationKey or None,
                'seq_length':           self.sequenceLength,
                'intra_seq_delimiter':  self.intraSeqDelim,
        }
        if units['annotation_key'] == u'(none)':
            units['annotation_key'] = None

        # Multiple values parameter...
        multipleValues = {
                'sort_order':           self.sortOrder,
                'reverse':              self.sortReverse,
                'keep_only_first':      self.keepOnlyFirst,
                'value_delimiter':      self.valueDelimiter,
        }

        # Contexts parameter...
        contexts = {
                'segmentation':         self.segmentations[self.contexts][1],
                'annotation_key':       self.contextAnnotationKey or None,
        }
        if contexts['annotation_key'] == u'(none)':
            contexts['annotation_key'] = None

        # Count...
        progressBar = OWGUI.ProgressBar(
                self,
                iterations = len(contexts['segmentation'])
        )
        table = self.processor.annotate_contexts(
                units,
                multipleValues,
                contexts,
                progress_callback   = progressBar.advance,
        )
        progressBar.finish()

        if not len(table.row_ids):
            self.infoBox.noDataSent(warning = u'Resulting table is empty.')
            self.send('Textable table', None)
        else:
            self.send('Textable table', table)
            self.infoBox.dataSent()

        self.sendButton.resetSettingsChangedFlag()


    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')

        if len(self.segmentations) == 0:
            self.units              = None
            self.unitAnnotationKey  = u''
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
            self.sequenceLengthSpin.control.setRange(
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
            self.contexts = self.contexts or 0
            segmentation = self.segmentations[self.contexts]
            self.contextAnnotationCombo.clear()
            self.contextAnnotationCombo.addItem(u'(none)')
            contextAnnotationKeys = segmentation[1].get_annotation_keys()
            for key in contextAnnotationKeys:
                self.contextAnnotationCombo.addItem(key)
            if self.contextAnnotationKey not in contextAnnotationKeys:
                self.contextAnnotationKey = u'(none)'
            self.contextAnnotationKey = self.contextAnnotationKey

        self.adjustSize()


    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext("", self.segmentations)
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


if __name__ == '__main__':
    from LTTL.Input         import Input
    from LTTL.Segmenter     import Segmenter
    import re
    appl = QApplication(sys.argv)
    ow   = OWTextableCategory()
    seg1 = Input(u'aaabc', 'text1')
    seg2 = Input(u'abbc', 'text2')
    segmenter = Segmenter()
    seg3 = segmenter.concatenate(
        [seg1, seg2],
        import_labels_as = 'string',
        label            = 'corpus'
    )
    seg4 = segmenter.tokenize(
        seg3,
        regexes = [(re.compile(r'\w+'),u'Tokenize',)],
    )
    seg5 = segmenter.tokenize(
        seg4,
        regexes = [(re.compile(r'[ai]'),u'Tokenize',)],
        label = 'V'
    )
    seg6 = segmenter.tokenize(
        seg4,
        regexes = [(re.compile(r'[bc]'),u'Tokenize',)],
        label = 'C'
    )
    seg7 = segmenter.concatenate(
        [seg5, seg6],
        import_labels_as    = 'category',
        label               = 'letters',
        sort                = True,
        merge_duplicates    = True,
    )
    ow.inputData(seg7, 1)
    ow.inputData(seg4, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
