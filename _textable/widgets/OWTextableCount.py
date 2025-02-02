"""
Class OWTextableCount
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

__version__ = '0.21.9'


from LTTL.TableThread import IntPivotCrosstab
from LTTL.Segmentation import Segmentation
import LTTL.ProcessorThread as Processor

from .TextableUtils import (
    OWTextableBaseWidget,
    InfoBox, SendButton, updateMultipleInputs, pluralize,
    SegmentationListContextHandler, SegmentationsInputList,
    Task
)

import Orange
from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableCount(OWTextableBaseWidget):
    """Orange widget for counting text units"""

    name = "Count"
    description = "Count segment types"
    icon = "icons/Count.png"
    priority = 8002

    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [
        ('Textable pivot crosstab', IntPivotCrosstab, widget.Default),
        ('Orange table', Orange.data.Table)
    ]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    segmentations = SegmentationsInputList()  # type: list

    # Settings...
    sequenceLength = settings.Setting(1)
    intraSeqDelim = settings.Setting(u'#')
    mode = settings.ContextSetting(u'No context')
    mergeContexts = settings.Setting(False)
    windowSize = settings.ContextSetting(1)
    leftContextSize = settings.ContextSetting(0)
    rightContextSize = settings.ContextSetting(0)
    mergeStrings = settings.Setting(False)
    unitPosMarker = settings.Setting(u'_')

    units = settings.ContextSetting(-1)
    unitAnnotationKey = settings.ContextSetting(u'(none)')
    _contexts = settings.ContextSetting(-1)
    contextAnnotationKey = settings.ContextSetting(u'(none)')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a Count widget"""
        super().__init__(*args, **kwargs)

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

        self.unitSegmentationCombo = gui.comboBox(
            widget=self.unitsBox,
            master=self,
            value='units',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segments will be counted.\n"
                u"This defines the columns of the resulting crosstab."
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
                u"Indicate whether the items to be counted in the\n"
                u"above specified segmentation are defined by the\n"
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
                u"Indicate whether to count single segments or\n"
                u"rather sequences of 2, 3, ... segments (n-grams)."
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

        # Contexts box...
        self.contextsBox = self.create_widgetbox(
            box=u'Contexts',
            orientation='vertical',
            addSpace=True,
            )

        self.modeCombo = gui.comboBox(
            widget=self.contextsBox,
            master=self,
            value='mode',
            sendSelectedValue=True,
            items=[
                u'No context',
                u'Sliding window',
                u'Left-right neighborhood',
                u'Containing segmentation',
            ],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
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
        self.slidingWindowBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.slidingWindowBox, height=3)
        self.windowSizeSpin = gui.spin(
            widget=self.slidingWindowBox,
            master=self,
            value='windowSize',
            minv=1,
            maxv=1,
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
        self.leftRightNeighborhoodBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.leftRightNeighborhoodBox, height=3)
        self.leftContextSizeSpin = gui.spin(
            widget=self.leftRightNeighborhoodBox,
            master=self,
            value='leftContextSize',
            minv=0,
            maxv=1,
            step=1,
            orientation='horizontal',
            label=u'Left context size:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The length of segment sequences defining the\n"
                u"left side of contexts."
            ),
        )
        gui.separator(widget=self.leftRightNeighborhoodBox, height=3)
        self.rightContextSizeSpin = gui.spin(
            widget=self.leftRightNeighborhoodBox,
            master=self,
            value='rightContextSize',
            minv=0,
            maxv=1,
            step=1,
            orientation='horizontal',
            label=u'Right context size:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The length of segment sequences defining the\n"
                u"right side of contexts."
            ),
        )
        gui.separator(widget=self.leftRightNeighborhoodBox, height=3)
        self.unitPosMarkerLineEdit = gui.lineEdit(
            widget=self.leftRightNeighborhoodBox,
            master=self,
            value='unitPosMarker',
            orientation='horizontal',
            label=u'Unit position marker:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"A (possibly empty) string that will be used to\n"
                u"indicate the separation between left and right\n"
                u"context sides."
            ),
        )
        gui.separator(widget=self.leftRightNeighborhoodBox, height=3)
        gui.checkBox(
            widget=self.leftRightNeighborhoodBox,
            master=self,
            value='mergeStrings',
            label=u'Treat distinct strings as contiguous',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box if you want to treat separate strings\n"
                u"as if they were actually contiguous, so that the end of\n"
                u"each string is adjacent to the beginning of the next string."
            ),
        )
        self.containingSegmentationBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(
            widget=self.containingSegmentationBox,
            height=3,
        )
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
                u"the contexts in which segments of the 'Units'\n"
                u"segmentation will be counted."
            ),
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        self.contextAnnotationCombo = gui.comboBox(
            widget=self.containingSegmentationBox,
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
        gui.separator(widget=self.containingSegmentationBox, height=3)
        gui.checkBox(
            widget=self.containingSegmentationBox,
            master=self,
            value='mergeContexts',
            label=u'Merge contexts',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box if you want to treat all segments\n"
                u"of the above specified segmentation as forming\n"
                u"a single context (hence the resulting crosstab\n"
                u"contains a single row)."
            ),
        )
        gui.separator(widget=self.contextsBox, height=3)

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

        # Send data treatment
        total = sum([i for i in textable_table.values.values()])
            
        if total == 0:
            self.infoBox.setText(u'Resulting table is empty.', 'warning')
            self.send('Textable pivot crosstab', None) # AS 10.2023: removed self
            self.send('Orange table', None) # AS 10.2023: removed self
        else:
            self.send('Textable pivot crosstab', textable_table) # AS 10.2023: removed self
            self.send('Orange table', orange_table) # AS 10.2023: removed self
                
            message = u'Table with %i occurrence@p sent to output.' % total
            message = pluralize(message, total)
            self.infoBox.setText(message)

    def sendData(self):
        """Check input, compute frequency tables, then send them"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Textable pivot crosstab', None) # AS 10.2023: removed self
            self.send('Orange table', None) # AS 10.2023: removed self
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

        # Infobox and progress bar
        self.infoBox.setText(u'Step 1/2: Processing...', 'warning')
        self.progressBarInit()

        # Case 1: sliding window...
        if self.mode == 'Sliding window':

            # Count...
            num_iterations = len(units['segmentation']) - (self.windowSize - 1)
            
            # Partial function for threading
            threaded_function = partial(
                Processor.count_in_window,
                caller=self,
                units=units,
                window_size=self.windowSize,
            )

        # Case 2: Left-right neighborhood...
        elif self.mode == 'Left-right neighborhood':

            # Count...
            num_iterations = (
                len(units['segmentation']) - (
                    self.leftContextSize +
                    self.sequenceLength +
                    self.rightContextSize - 1
                )
            )

            # Partial function for threading
            threaded_function = partial(
                Processor.count_in_chain,
                caller=self,
                units=units,
                contexts={
                    'left_size': self.leftContextSize,
                    'right_size': self.rightContextSize,
                    'unit_pos_marker': self.unitPosMarker,
                    'merge_strings': self.mergeStrings,
                },
            )

        # Case 3: Containing segmentation or no context...
        else:

            # Parameters for mode 'Containing segmentation'...
            if self.mode == 'Containing segmentation':
                assert self._contexts >= 0
                contexts = {
                    'segmentation': self.segmentations[self._contexts][1],
                    'annotation_key': self.contextAnnotationKey or None,
                    'merge': self.mergeContexts,
                }
                if contexts['annotation_key'] == u'(none)':
                    contexts['annotation_key'] = None
                num_iterations = len(contexts['segmentation'])
            # Parameters for mode 'No context'...
            else:
                contexts = None
                num_iterations = (
                    len(units['segmentation']) - (self.sequenceLength - 1)
                )
        
            # Partial function for threading
            threaded_function = partial(
                Processor.count_in_context,
                caller=self,
                units=units,
                contexts=contexts,
            )

        # Threading
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
        self.updateGUI() # Call get_annotation_keys (multiple times?)

    def onInputRemoval(self, index):
        """Handle removal of input with given index"""
        if index < self.units:
            self.units -= 1
        elif index == self.units and self.units == len(self.segmentations) - 1:
            self.units -= 1
        if self.mode == u'Containing segmentation':
            if index == self._contexts:
                self.mode = u'No context'
                self._contexts = -1
            elif index < self._contexts:
                self._contexts -= 1
                if self._contexts < 0:
                    self.mode = u'No context'

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
            self.units = -1
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
            self.mode = 'No context'
            self.contextsBox.setDisabled(True)
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

        if self.mode == u'Sliding window':
            self.containingSegmentationBox.setVisible(False)
            self.leftRightNeighborhoodBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)

            self.windowSizeSpin.setRange(
                self.sequenceLength,
                len(self.segmentations[self.units][1])
            )
            self.windowSize = self.windowSize or 1

        elif self.mode == u'Left-right neighborhood':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(False)
            self.leftRightNeighborhoodBox.setVisible(True)
            self.leftContextSizeSpin.setRange(
                0,
                len(self.segmentations[self.units][1]) -
                self.sequenceLength -
                self.rightContextSize
            )
            self.leftContextSize = self.leftContextSize or 0
            self.rightContextSizeSpin.setRange(
                0,
                len(self.segmentations[self.units][1]) -
                self.sequenceLength - self.leftContextSize
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

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.openContext(self.uuid, self.segmentations) # Optimized by AX in Segmentation.py (30.08.2023)
        self.updateGUI()
        self.sendButton.sendIf()

if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication
    import LTTL.Segmenter as Segmenter
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableCount()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'cruel world', label=u'text2')
    seg3 = Segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = Segmenter.tokenize(
        seg3,
        [(r'\w+(?u)', u'tokenize', {'type': 'mot'})],
        label=u'words'
    )
    ow.inputData(seg3, 1)
    ow.inputData(seg4, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
