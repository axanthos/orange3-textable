#=============================================================================
# Class OWTextableCount
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

__version__ = '0.21'

"""
<name>Count</name>
<description>Count segment types</description>
<icon>icons/Count.png</icon>
<priority>8001</priority>
"""

from LTTL.Table        import IntPivotCrosstab
from LTTL.Processor    import Processor
from LTTL.Segmentation import Segmentation

from TextableUtils     import *

import Orange
from Orange.OrangeWidgets.OWWidget import *
import OWGUI

class OWTextableCount(OWWidget):

    """Orange widget for counting text units"""

    contextHandlers = {
        '': SegmentationListContextHandler(
            '', [
                ContextInputListField('segmentations'),
                ContextInputIndex('units'),
                ContextInputIndex('contexts'),
                'mode',
                'unitAnnotationKey',
                'contextAnnotationKey',
                'sequenceLength',
                'windowSize',
                'leftContextSize',
                'rightContextSize',
                'uuid',
            ]
        )
    }

    settingsList = [
            'autoSend',
            'intraSeqDelim',
            'unitPosMarker',
            'mergeContexts',
            'sequenceLength',
            'windowSize',
            'leftContextSize',
            'rightContextSize',
    ]

    def __init__(self, parent=None, signalManager=None):
        
        """Initialize a Count widget"""

        OWWidget.__init__(
                self,
                parent,
                signalManager,
                wantMainArea=0,
        )
        
        self.inputs  = [('Segmentation', Segmentation, self.inputData, Multiple)]
        self.outputs = [('Pivot Crosstab', IntPivotCrosstab)]
        
        # Settings...
        self.autoSend                   = False
        self.sequenceLength             = 1
        self.intraSeqDelim              = u'#'
        self.mode                       = u'No context'
        self.mergeContexts              = False
        self.windowSize                 = 1
        self.leftContextSize            = 0
        self.rightContextSize           = 0
        self.unitPosMarker              = u'_'
        self.uuid                       = None
        self.loadSettings()
        self.uuid = getWidgetUuid(self)




        # Other attributes...
        self.processor              = Processor()
        self.segmentations          = []
        self.units                  = None
        self.unitAnnotationKey      = None
        self.contexts               = None
        self.contextAnnotationKey   = None
        self.infoBox                = InfoBox(
                widget          = self.controlArea,
                stringClickSend = u"Please click 'Compute' when ready.",
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
                        u"The segmentation whose segments will be counted.\n"
                        u"This defines the columns of the resulting crosstab."
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
                        u"Indicate whether the items to be counted in the\n"
                        u"above specified segmentation are defined by the\n"
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
                        u"Indicate whether to count single segments or\n"
                        u"rather sequences of 2, 3, ... segments (n-grams)."
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

        # Contexts box...
        self.contextsBox = OWGUI.widgetBox(
                widget              = self.controlArea,
                box                 = u'Contexts',
                orientation         = 'vertical',
                addSpace            = True,
        )
        self.modeCombo = OWGUI.comboBox(
                widget              = self.contextsBox,
                master              = self,
                value               = 'mode',
                sendSelectedValue   = True,
                items               = [
                        u'No context',
                        u'Sliding window',
                        u'Left-right neighborhood',
                        u'Containing segmentation',
                ],
                orientation         = 'horizontal',
                label               = u'Mode:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Context specification mode.\n\n"
                        u"Contexts define the rows of the resulting\n"
                        u"crosstab.\n\n"
                        u"'No context': segments will be counted\n"
                        u"irrespective of their context (hence the output\n"
                        u"table contains a single row).\n\n"
                        u"'Sliding window': contexts are defined as all the\n"
                        u"successive, overlapping sequences of n segments\n"
                        u"in the 'Units' segmentation.\n\n"
                        u"'Left-right neighborhood': contexts are defined as\n"
                        u"distinct combinations of segments occurring\n"
                        u"immediately to the right and/or left of segments\n"
                        u"in the 'Units' segmentation.\n\n"
                        u"'Containing segmentation': contexts are defined\n"
                        u"as the distinct segments occurring in a given\n"
                        u"segmentation (which may or may not be the same\n"
                        u"as the 'Units' segmentation)."
                ),
        )
        self.slidingWindowBox = OWGUI.widgetBox(
                widget              = self.contextsBox,
                orientation         = 'vertical',
        )
        OWGUI.separator(
                widget              = self.slidingWindowBox,
                height              = 3,
        )
        self.windowSizeSpin = OWGUI.spin(
                widget              = self.slidingWindowBox,
                master              = self,
                value               = 'windowSize',
                min                 = 1,
                max                 = 1,
                step                = 1,
                orientation         = 'horizontal',
                label               = u'Window size:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The length of segment sequences defining contexts."
                ),
        )
        self.leftRightNeighborhoodBox = OWGUI.widgetBox(
                widget              = self.contextsBox,
                orientation         = 'vertical',
        )
        OWGUI.separator(
                widget              = self.leftRightNeighborhoodBox,
                height              = 3,
        )
        self.leftContextSizeSpin = OWGUI.spin(
                widget              = self.leftRightNeighborhoodBox,
                master              = self,
                value               = 'leftContextSize',
                min                 = 0,
                max                 = 1,
                step                = 1,
                orientation         = 'horizontal',
                label               = u'Left context size:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The length of segment sequences defining the\n"
                        u"left side of contexts."
                ),
        )
        OWGUI.separator(
                widget              = self.leftRightNeighborhoodBox,
                height              = 3,
        )
        self.rightContextSizeSpin = OWGUI.spin(
                widget              = self.leftRightNeighborhoodBox,
                master              = self,
                value               = 'rightContextSize',
                min                 = 0,
                max                 = 1,
                step                = 1,
                orientation         = 'horizontal',
                label               = u'Right context size:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The length of segment sequences defining the\n"
                        u"right side of contexts."
                ),
        )
        OWGUI.separator(
                widget              = self.leftRightNeighborhoodBox,
                height              = 3,
        )
        self.unitPosMarkerLineEdit = OWGUI.lineEdit(
                widget              = self.leftRightNeighborhoodBox,
                master              = self,
                value               = 'unitPosMarker',
                orientation         = 'horizontal',
                label               = u'Unit position marker:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"A (possibly empty) string that will be used to\n"
                        u"indicate the separation between left and right\n"
                        u"context sides."
                ),
        )
        self.containingSegmentationBox = OWGUI.widgetBox(
                widget              = self.contextsBox,
                orientation         = 'vertical',
        )
        OWGUI.separator(
                widget              = self.containingSegmentationBox,
                height              = 3,
        )
        self.contextSegmentationCombo = OWGUI.comboBox(
                widget              = self.containingSegmentationBox,
                master              = self,
                value               = 'contexts',
                orientation         = 'horizontal',
                label               = u'Segmentation:',
                labelWidth          = 180,
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"The segmentation whose segment types define\n"
                        u"the contexts in which segments of the 'Units'\n"
                        u"segmentation will be counted."
                ),
        )
        OWGUI.separator(
                widget              = self.containingSegmentationBox,
                height              = 3,
        )
        self.contextAnnotationCombo = OWGUI.comboBox(
                widget              = self.containingSegmentationBox,
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
                widget              = self.containingSegmentationBox,
                height              = 3,
        )
        OWGUI.checkBox(
                widget              = self.containingSegmentationBox,
                master              = self,
                value               = 'mergeContexts',
                label               = u'Merge contexts',
                callback            = self.sendButton.settingsChanged,
                tooltip             = (
                        u"Check this box if you want to treat all segments\n"
                        u"of the above specified segmentation as forming\n"
                        u"a single context (hence the resulting crosstab\n"
                        u"contains a single row)."
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
        if self.mode == u'Containing segmentation':
            if index == self.contexts:
                self.mode       = u'No context'
                self.contexts   = None
            elif index < self.contexts:
                self.contexts -= 1
                if self.contexts < 0:
                    self.mode     = u'No context'
                    self.contexts = None


    def sendData(self):

        """Check input, compute frequency tables, then send them"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.noDataSent(u'No input.')
            self.send('Pivot Crosstab', None)
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

        # Case 1: sliding window...
        if self.mode == 'Sliding window':

            # Count...
            progressBar = OWGUI.ProgressBar(
                    self,
                    iterations = len(units['segmentation'])
                               - (self.windowSize - 1)
            )
            table = self.processor.count_in_window(
                    units,
                    window_size         = self.windowSize,
                    progress_callback   = progressBar.advance,
            )
            progressBar.finish()

        # Case 2: Left-right neighborhood...
        elif self.mode == 'Left-right neighborhood':

            # Count...
            num_iterations = (
                    len(units['segmentation'])
                  - (
                            self.leftContextSize
                          + self.sequenceLength
                          + self.rightContextSize
                          - 1
                    )
            )
            progressBar = OWGUI.ProgressBar(
                    self,
                    iterations = num_iterations
            )
            table = self.processor.count_in_chain(
                    units,
                    contexts = {
                        'left_size':        self.leftContextSize,
                        'right_size':       self.rightContextSize,
                        'unit_pos_marker':  self.unitPosMarker,
                    },
                    progress_callback   = progressBar.advance,
            )
            progressBar.finish()

        # Case 3: Containing segmentation or no context...
        else:

            # Parameters for mode 'Containing segmentation'...
            if self.mode == 'Containing segmentation':
                contexts = {
                    'segmentation':     self.segmentations[self.contexts][1],
                    'annotation_key':   self.contextAnnotationKey or None,
                    'merge':            self.mergeContexts,
                }
                if contexts['annotation_key'] == u'(none)':
                    contexts['annotation_key'] = None
                num_iterations = len(contexts['segmentation'])
            # Parameters for mode 'No context'...
            else:
                contexts = None
                num_iterations = (
                                        len(units['segmentation'])
                                      - (self.sequenceLength - 1)
                                 )

            # Count...
            progressBar = OWGUI.ProgressBar(
                    self,
                    iterations = num_iterations
            )
            table = self.processor.count_in_context(
                    units,
                    contexts,
                    progress_callback   = progressBar.advance,
            )
            progressBar.finish()

        totalCount = sum([i for i in table.values.values()])
        if totalCount == 0:
            self.infoBox.noDataSent(u'Total count is 0.')
            self.send('Pivot Crosstab', None)
        else:
            self.send('Pivot Crosstab', table)
            self.infoBox.dataSent(u'Total count is %i.' % totalCount)

        self.sendButton.resetSettingsChangedFlag()


    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')

        if self.mode == u'No context':
            self.containingSegmentationBox.setVisible(False)
            self.leftRightNeighborhoodBox.setVisible(False)
            self.slidingWindowBox.setVisible(False)

        if len(self.segmentations) == 0:
            self.units              = None
            self.unitAnnotationKey  = u''
            self.unitsBox.setDisabled(True)
            self.mode               = 'No context'
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

        if self.mode == u'Sliding window':
            self.containingSegmentationBox.setVisible(False)
            self.leftRightNeighborhoodBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)

            self.windowSizeSpin.control.setRange(
                    self.sequenceLength,
                    len(self.segmentations[self.units][1])
            )
            self.windowSize = self.windowSize or 1

        elif self.mode == u'Left-right neighborhood':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(False)
            self.leftRightNeighborhoodBox.setVisible(True)
            self.leftContextSizeSpin.control.setRange(
                    0,
                    len(self.segmentations[self.units][1])
                  - self.sequenceLength
                  - self.rightContextSize
            )
            self.leftContextSize = self.leftContextSize or 0
            self.rightContextSizeSpin.control.setRange(
                    0,
                    len(self.segmentations[self.units][1])
                  - self.sequenceLength
                  - self.leftContextSize
            )
            self.rightContextSize = self.rightContextSize or 0

        elif self.mode == u'Containing segmentation':
            self.slidingWindowBox.setVisible(False)
            self.leftRightNeighborhoodBox.setVisible(False)
            self.containingSegmentationBox.setVisible(True)
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
        settings["settingsDataVersion"] = __version__.split('.')
        return settings

    def setSettings(self, settings):
        if settings.get("settingsDataVersion", None) == __version__.split('.'):
            settings = settings.copy()
            del settings["settingsDataVersion"]
            OWWidget.setSettings(self, settings)


if __name__ == '__main__':
    from LTTL.Segmenter import Segmenter
    from LTTL.Input     import Input
    appl = QApplication(sys.argv)
    ow   = OWTextableCount()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'cruel world', label=u'text2')
    segmenter = Segmenter()
    seg3 = segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = segmenter.tokenize(seg3, [(r'\w+(?u)',u'tokenize',{'type':'mot'})], label=u'words')
    ow.inputData(seg3, 1)
    ow.inputData(seg4, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
