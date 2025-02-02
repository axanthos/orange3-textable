"""
Class OWTextableLength
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

__version__ = '0.14.7'


from LTTL.TableThread import Table
from LTTL.Segmentation import Segmentation
import LTTL.ProcessorThread as Processor

from .TextableUtils import (
    OWTextableBaseWidget, SegmentationListContextHandler, ProgressBar,
    SegmentationsInputList, InfoBox, SendButton, updateMultipleInputs,
    Task
)

import Orange
import Orange.data
from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableLength(OWTextableBaseWidget):
    """Orange widget for length computation"""

    name = "Length"
    description = "Compute the (average) length of segments"
    icon = "icons/Length.png"
    priority = 8003

    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [('Textable table', Table, widget.Default),
               ('Orange table', Orange.data.Table)]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    segmentations = SegmentationsInputList()  # type: list

    # Settings...
    computeAverage = settings.Setting(False)
    computeStdev = settings.Setting(False)
    mergeContexts = settings.Setting(False)

    units = settings.ContextSetting(-1)
    averagingSegmentation = settings.ContextSetting(-1)
    _contexts = settings.ContextSetting(-1)
    mode = settings.ContextSetting(u'No context')
    contextAnnotationKey = settings.ContextSetting(u'(none)')

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a Length widget"""
        super().__init__(*args, **kwargs)
        
        # Manual cancel (cancel button)
        manualCancel = partial(self.cancel, True) # True = "Aborted by user!"

        self.windowSize = 1

        self.infoBox = InfoBox(
            widget=self.controlArea,
            stringClickSend=u", please click 'Send' when ready.",
        )
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=manualCancel, # Manual cancel button
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
            labelWidth=190,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segments constitute the\n"
                u"units of length."
            ),
        )
        self.unitSegmentationCombo.setMinimumWidth(120)
        gui.separator(widget=self.unitsBox, height=3)

        # Averaging box...
        self.averagingBox = self.create_widgetbox(
            box=u'Averaging',
            orientation='vertical',
            addSpace=True,
            )

        averagingBoxLine1 = gui.widgetBox(
            widget=self.averagingBox,
            box=False,
            orientation='horizontal',
            addSpace=True,
        )
        gui.checkBox(
            widget=averagingBoxLine1,
            master=self,
            value='computeAverage',
            label=u'Average over segmentation:',
            labelWidth=190,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box in order to measure the average\n"
                u"length of segments.\n\n"
                u"Leaving this box unchecked implies that no\n"
                u"averaging will take place."
            ),
        )
        self.averagingSegmentationCombo = gui.comboBox(
            widget=averagingBoxLine1,
            master=self,
            value='averagingSegmentation',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segment length will be\n"
                u"measured and averaged (if the box to the left\n"
                u"is checked)."
            ),
        )
        self.computeStdevCheckBox = gui.checkBox(
            widget=self.averagingBox,
            master=self,
            value='computeStdev',
            label=u'Compute standard deviation',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Check this box to compute not only length average\n"
                u"but also standard deviation (if the above box\n"
                u"is checked).\n\n"
                u"Note that computing standard deviation can be a\n"
                u"lengthy operation for large segmentations."
            ),
        )
        gui.separator(widget=self.averagingBox, height=2)

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
                u'Containing segmentation',
            ],
            orientation='horizontal',
            label=u'Mode:',
            labelWidth=190,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Context specification mode.\n\n"
                u"Contexts define the rows of the resulting table.\n\n"
                u"'No context': simply return the length of the\n"
                u"'Units' segmentation, or the average length of\n"
                u"segments in the 'Averaging' segmentation (if any),\n"
                u"so that the output table contains a single row.\n\n"
                u"'Sliding window': contexts are defined as all the\n"
                u"successive, overlapping sequences of n segments\n"
                u"in the 'Averaging' segmentation; this mode is\n"
                u"available only if the 'Averaging' box is checked.\n\n"
                u"'Containing segmentation': contexts are defined\n"
                u"as the distinct segments occurring in a given\n"
                u"segmentation (which may or may not be the same\n"
                u"as the 'Units' and/or 'Averaging' segmentation)."
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
            labelWidth=190,
            callback=self.sendButton.settingsChanged,
            keyboardTracking=False,
            tooltip=(
                u"The length of segment sequences defining contexts."
            ),
        )
        self.containingSegmentationBox = gui.widgetBox(
            widget=self.contextsBox,
            orientation='vertical',
        )
        gui.separator(widget=self.containingSegmentationBox, height=3)
        self.contextSegmentationCombo = gui.comboBox(
            widget=self.containingSegmentationBox,
            master=self,
            value='_contexts',
            orientation='horizontal',
            label=u'Segmentation:',
            labelWidth=190,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"The segmentation whose segment types define\n"
                u"the contexts in which length will be measured."
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
            labelWidth=190,
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
                u"a single context (hence the resulting table\n"
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
            
        # Processing results
        if not len(textable_table.row_ids):
            self.infoBox.setText(u'Resulting table is empty.', 'warning')
            self.send('Textable table', None) # AS 10.2023: removed self
            self.send('Orange table', None) # AS 10.2023: removed self
        else:
            self.infoBox.setText(u'Table sent to output.')
            self.send('Textable table', textable_table) # AS 10.2023: removed self
            self.send('Orange table', orange_table) # AS 10.2023: removed self

    def sendData(self):

        """Check input, compute (average) length table, then send it"""

        # Check that there's something on input...
        if len(self.segmentations) == 0:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Textable table', None) # AS 10.2023: removed self
            self.send('Orange table', None) # AS 10.2023: removed self
            return
        assert self.units >= 0

        # Units parameter...
        units = self.segmentations[self.units][1]

        # Averaging parameters...
        if self.computeAverage:
            assert self.averagingSegmentation >= 0
            averaging = {
                'segmentation':self.segmentations[self.averagingSegmentation][1]
            }
            if self.computeStdev:
                averaging['std_deviation'] = True
            else:
                averaging['std_deviation'] = False
        else:
            averaging = None
            
        # Infobox and progress bar
        self.infoBox.setText(u'Step 1/2: Processing...', 'warning')
        self.progressBarInit()

        # Case 1: sliding window...
        if self.mode == 'Sliding window':

            # Progress bar
            Orange.widgets.gui.ProgressBar(
                self,
                iterations=len(units) - (self.windowSize - 1)
            )
            
            # Compute length...
            # Partial function for threading
            threaded_function = partial(
                Processor.length_in_window,
                caller=self,
                units=units,
                averaging=averaging,
                window_size=self.windowSize,
            )

        # Case 2: Containing segmentation or no context...
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
                num_iterations = 1
            
            # Progress bar
            Orange.widgets.gui.ProgressBar(
                self,
                iterations=num_iterations
            )
            
            # Compute length...
            # Partial function for threading
            threaded_function = partial(
                Processor.length_in_context,
                caller=self,
                units=units,
                averaging=averaging,
                contexts=contexts,
            )

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
        if self.mode == u'Containing segmentation':
            if index == self._contexts:
                self.mode = u'No context'
                self._contexts = -1
            elif index < self._contexts:
                self._contexts -= 1
                if self._contexts < 0:
                    self.mode = u'No context'
        if self.computeAverage \
                and self.averagingSegmentation != self.units:
            if index == self.averagingSegmentation:
                self.computeAverage = False
                self.averagingSegmentation = -1
            elif index < self.averagingSegmentation:
                self.averagingSegmentation -= 1
                if self.averagingSegmentation < 0:
                    self.computeAverage = False

    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.averagingSegmentationCombo.clear()
        self.averagingSegmentationCombo.clear()

        if self.mode == u'No context':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(False)

        if len(self.segmentations) == 0:
            self.units = -1
            self.unitsBox.setDisabled(True)
            self.averagingBox.setDisabled(True)
            self.mode = 'No context'
            self.contextsBox.setDisabled(True)
            return
        else:
            if len(self.segmentations) == 1:
                self.units = 0
                self.averagingSegmentation = 0
            for segmentation in self.segmentations:
                self.unitSegmentationCombo.addItem(segmentation[1].label)
                self.averagingSegmentationCombo.addItem(segmentation[1].label)
            self.units = max(self.units, 0)
            self.averagingSegmentation = max(self.averagingSegmentation, 0)
            self.unitsBox.setDisabled(False)
            self.averagingBox.setDisabled(False)
            self.contextsBox.setDisabled(False)
            if self.computeAverage:
                if self.modeCombo.itemText(1) != u'Sliding window':
                    self.modeCombo.insertItem(1, u'Sliding window')
                self.averagingSegmentationCombo.setDisabled(False)
                self.computeStdevCheckBox.setDisabled(False)
            else:
                self.averagingSegmentationCombo.setDisabled(True)
                self.computeStdevCheckBox.setDisabled(True)
                self.computeStdev = False
                if self.mode == u'Sliding window':
                    self.mode = u'No context'
                if self.modeCombo.itemText(1) == u'Sliding window':
                    self.modeCombo.removeItem(1)

        if self.mode == 'Sliding window':
            self.containingSegmentationBox.setVisible(False)
            self.slidingWindowBox.setVisible(True)
            self.windowSizeSpin.setRange(
                1,
                len(self.segmentations[self.units][1])
            )
            self.windowSize = self.windowSize or 1

        elif self.mode == 'Containing segmentation':
            self.slidingWindowBox.setVisible(False)
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
        self.openContext(self.uuid, self.segmentations)
        self.updateGUI()
        self.sendButton.sendIf()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    import LTTL.Segmenter as Segmenter
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableLength()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'wonderful world', label=u'text2')
    seg3 = Segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = Segmenter.tokenize(
        seg3,
        [(r'\w+(?u)', u'tokenize',)],
        label=u'words'
    )
    seg5 = Segmenter.tokenize(seg3, [(r'\w', u'tokenize',)], label=u'letters')
    ow.inputData(seg3, 1)
    ow.inputData(seg4, 2)
    ow.inputData(seg5, 3)
    ow.show()
    appl.exec_()
    ow.saveSettings()
