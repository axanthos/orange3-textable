"""
Class OWTextableCategory
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

__version__ = '0.12.6'

from LTTL.TableThread import Table
from LTTL.Segmentation import Segmentation
import LTTL.ProcessorThread as Processor

from .TextableUtils import (
    OWTextableBaseWidget, ProgressBar,
    InfoBox, SendButton, updateMultipleInputs, SegmentationListContextHandler,
    SegmentationsInputList,
    Task
)

import Orange.data
from Orange.widgets import widget, gui, settings

# Threading
from AnyQt.QtCore import QThread, pyqtSlot, pyqtSignal
import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableCategory(OWTextableBaseWidget):
    """Orange widget for extracting content or annotation information"""

    # Signals
    signal_prog = pyqtSignal((int, bool))       # Progress bar (value, init)
    signal_text = pyqtSignal((str, str))        # Text label (text, infotype)
    signal_cancel_button = pyqtSignal(bool)     # Allow to Deactivate cancel
                                                # button from worker thread

    name = "Category"
    description = "Build a table with categories defined by segments' " \
                  "content or annotations."
    icon = "icons/Category.png"
    priority = 8006

    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [('Textable table', Table, widget.Default),
               ('Orange table', Orange.data.Table)]

    settingsHandler = SegmentationListContextHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    segmentations = SegmentationsInputList()  # type: list

    intraSeqDelim = settings.Setting(u'#')
    sortOrder = settings.Setting(u'Frequency')
    sortReverse = settings.Setting(True)
    keepOnlyFirst = settings.Setting(True)
    valueDelimiter = settings.Setting(u'|')

    units = settings.ContextSetting(-1)
    _contexts = settings.ContextSetting(-1)
    unitAnnotationKey = settings.ContextSetting(u'(none)')
    contextAnnotationKey = settings.ContextSetting(u'(none)')
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
            cancelCallback=self.cancel_manually,
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
        
        # Threading
        self._task = None
        self._executor = ThreadExecutor()
        self.cancel_operation = False

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

        # Connect signals to slots
        self.signal_prog.connect(self.update_progress_bar) 
        self.signal_text.connect(self.update_infobox)
        self.signal_cancel_button.connect(self.disable_cancel_button)
        
    @pyqtSlot(concurrent.futures.Future)
    def _task_finished(self, f):    
        assert self.thread() is QThread.currentThread()
        assert self._task is not None
        assert self._task.future is f
        assert f.done()

        self._task = None

        try:
            # Table outputs
            textable_table, orange_table = f.result()

            # Send data
            if not len(textable_table.row_ids):
                self.infoBox.setText(u'Resulting table is empty.', 'warning')
                self.send('Textable table', None)
                self.send('Orange table', None)
            else:
                self.infoBox.setText(u'Table sent to output.')
                self.send('Textable table', textable_table)
                self.send('Orange table', orange_table)

        except Exception as ex:
            print(ex)

            # Send None
            self.send('Textable table', None)
            self.send('Orange table', None)
            self.infoBox.setText(u'An error occured.', 'error')

        finally:
            # Manage GUI visibility
            self.manageGuiVisibility(False) # Processing done/cancelled!

    def cancel_manually(self):
        """ Wrapper of cancel() method,
        used for manual cancellations """
        self.cancel(manualCancel=True)

    def cancel(self, manualCancel=False):
        # Make loop break in LTTL/ProcessorThread.py 
        self.cancel_operation = True

        # Cancel current task
        if self._task is not None:
            self._task.cancel()
            assert self._task.future.done()
            
            # Disconnect slot
            self._task.watcher.done.disconnect(self._task_finished)
            self._task = None
            
            # Send None to output
            self.send('Textable table', None)
            self.send('Orange table', None)

        # If cancelled manually
        if manualCancel:
            self.infoBox.setText(u'Operation cancelled by user.', 'warning')

        # Manage GUI visibility
        self.manageGuiVisibility(False) # Processing done/cancelled

    def manageGuiVisibility(self, processing=False):
        """ Update GUI and make available (or not) elements
        while the thread task is running in background """
        
        # Thread currently running, freeze the GUI
        if processing:
            self.sendButton.cancelButton.setDisabled(0) # Cancel: ENABLED
            self.sendButton.mainButton.setDisabled(1) # Send: DISABLED
            self.sendButton.autoSendCheckbox.setDisabled(1) # Send automatically: DISABLED
            self.unitsBox.setDisabled(1) # Units box: DISABLED
            self.multipleValuesBox.setDisabled(1) # Multiple value box: DISABLED
            self.contextsBox.setDisabled(1) # Contexts box: DISABLED
            

        # Thread done or not running, unfreeze the GUI
        else:
            # If "Send automatically" is disabled, reactivate "Send" button
            if not self.sendButton.autoSendCheckbox.isChecked():
                self.sendButton.mainButton.setDisabled(0) # Send: ENABLED
            # Other buttons and layout
            self.sendButton.cancelButton.setDisabled(1) # Cancel: DISABLED
            self.sendButton.autoSendCheckbox.setDisabled(0) # Send automatically: DISABLED
            self.unitsBox.setDisabled(0) # Units box: ENABLED
            self.multipleValuesBox.setDisabled(0) # Multiple value box: ENABLED
            self.contextsBox.setDisabled(0) # Contexts box: ENABLED
            self.cancel_operation = False # Restore to default
            self.signal_prog.emit(100, False) # 100% and do not re-init
            self.sendButton.resetSettingsChangedFlag()
            self.updateGUI()

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
        assert self._contexts >= 0
        contexts = {
            'segmentation': self.segmentations[self._contexts][1],
            'annotation_key': self.contextAnnotationKey or None,
        }
        if contexts['annotation_key'] == u'(none)':
            contexts['annotation_key'] = None

        # Count...
        self.infoBox.setText(u"Step 1/3: Pre-processing (count units)...", "warning")

        # Partial function for threading
        threaded_function = partial(
            Processor.annotate_contexts,
            caller=self,
            units=units,
            multiple_values=multipleValues,
            contexts=contexts,
            iterations=len(contexts['segmentation']),
        )

        # Threading ...
        
        # Cancel old tasks
        if self._task is not None:
            self.cancel()
        assert self._task is None

        self._task = task = Task()
        
        # Restore to default
        self.cancel_operation = False

        # Threading start, future, and watcher
        task.future = self._executor.submit(threaded_function)
        task.watcher = FutureWatcher(task.future)
        task.watcher.done.connect(self._task_finished)
        
        # Manage GUI visibility
        self.manageGuiVisibility(True) # Processing

    # AS 11.2023
    @pyqtSlot(int, bool)
    def update_progress_bar(self, val, init):
        """ Update progress bar in a thread-safe manner """
        # Re-init progress bar, if needed
        if init:
            self.progressBarInit()
        
        # Update progress bar
        if val >= 100:
            self.progressBarFinished() # Finish progress bar     
        elif val < 0:
            self.progressBarSet(0)
        else:
            self.progressBarSet(val)

    # AS 11.2023
    @pyqtSlot(str, str)
    def update_infobox(self, text, infotype):
        """ Update info box in a thread-safe manner """
        self.infoBox.setText(text, infotype)

    # AS 11.2023
    @pyqtSlot(bool)
    def disable_cancel_button(self, disable):
        """ Disables cancel button in a thread-safe manner """
        if disable:
            self.sendButton.cancelButton.setDisabled(1)
        else:
            self.sendButton.cancelButton.setDisabled(0)

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
        if index == self._contexts:
            self.mode = u'No context'
            self._contexts = -1
        elif index < self._contexts:
            self._contexts -= 1
            if self._contexts < 0:
                self.mode = u'No context'
                self._contexts = -1

    def updateGUI(self):

        """Update GUI state"""

        self.unitSegmentationCombo.clear()
        self.unitAnnotationCombo.clear()
        self.unitAnnotationCombo.addItem(u'(none)')

        if len(self.segmentations) == 0:
            self.units = -1
            self.unitAnnotationKey = u''
            self.unitsBox.setDisabled(True)
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
    import re
    from PyQt5.QtWidgets import QApplication
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
