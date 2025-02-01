"""
Class OWTextableMerge
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

__version__ = '0.21.4'


from LTTL.Segmentation import Segmentation
import LTTL.SegmenterThread as Segmenter

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    updateMultipleInputs, InfoBox, SendButton, pluralize,
    Task
)

from Orange.widgets import widget, gui, settings

# Threading
from AnyQt.QtCore import QThread, pyqtSlot, pyqtSignal
import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableMerge(OWTextableBaseWidget):
    """Orange widget for merging segmentations"""
    
    # AS 10.2023
    # Signals
    signal_prog = pyqtSignal((int, bool))       # Progress bar (value, init)
    signal_text = pyqtSignal((str, str))        # Text label (text, infotype)

    name = "Merge"
    description = "Merge two or more segmentations"
    icon = "icons/Merge.png"
    priority = 4001

    # Input and output channels...
    inputs = [('Segmentation', Segmentation, "inputData", widget.Multiple)]
    outputs = [('Merged data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )
    # Settings...
    importLabels = settings.Setting(True)
    labelKey = settings.Setting(u'source')     # TODO update docs
    autoNumber = settings.Setting(False)
    autoNumberKey = settings.Setting(u'num')
    copyAnnotations = settings.Setting(True)
    mergeDuplicates = settings.Setting(False)

    want_main_area = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.texts = list()
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually,
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Options box...
        self.optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=False,
        )
        optionsBoxLine1 = gui.widgetBox(
            widget=self.optionsBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=optionsBoxLine1,
            master=self,
            value='importLabels',
            label=u'Import labels with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Import labels of input segmentations as annotations."
            ),
        )
        self.labelKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine1,
            master=self,
            value='labelKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for importing input segmentation\n"
                u"labels."
            ),
        )
        gui.separator(widget=self.optionsBox, height=3)
        optionsBoxLine2 = gui.widgetBox(
            widget=self.optionsBox,
            box=False,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumber',
            label=u'Auto-number with key:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotate input segments with increasing numeric\n"
                u"indices\n\n"
                u"Note that a distinct index will be assigned to\n"
                u"each segment of each input segmentation."
            ),
        )
        self.autoNumberKeyLineEdit = gui.lineEdit(
            widget=optionsBoxLine2,
            master=self,
            value='autoNumberKey',
            orientation='horizontal',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Annotation key for input segment auto-numbering."
            ),
        )
        gui.separator(widget=self.optionsBox, height=3)
        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value='copyAnnotations',
            label=u'Copy annotations',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Copy all annotations from input to output segments."
            ),
        )
        gui.separator(widget=self.optionsBox, height=3)
        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value='mergeDuplicates',
            label=u'Fuse duplicates',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Fuse segments that have the same address.\n\n"
                u"The annotation of merged segments will be fused\n"
                u"as well. In the case where fused segments have\n"
                u"distinct values for the same annotation key, only\n"
                u"the value of the last one (in address order)\n"
                u"will be kept."
            ),
        )
        gui.separator(widget=self.optionsBox, height=2)
        gui.separator(widget=self.controlArea, height=3)

        gui.rubber(self.controlArea)
        
        # Threading
        self._task = None
        self._executor = ThreadExecutor()
        self.cancel_operation = False

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        
        # Connect signals to slots
        self.signal_prog.connect(self.update_progress_bar) 
        self.signal_text.connect(self.update_infobox)

    @pyqtSlot(concurrent.futures.Future)
    def _task_finished(self, f):    
        assert self.thread() is QThread.currentThread()
        assert self._task is not None
        assert self._task.future is f
        assert f.done()

        self._task = None

        try:
            # Table outputs
            concatenation = f.result()

            # Send data treatment
            message = u'%i segment@p sent to output.' % len(concatenation)
            message = pluralize(message, len(concatenation))
            self.infoBox.setText(message)
            self.send('Merged data', concatenation) # AS 10.2023: removed self

        except Exception as ex:
            print(ex)

            # Send None
            self.send('Merged data', None) # AS 10.2023: removed self
            self.infoBox.setText(u'An error occured.', 'warning')

        finally:
            # Manage GUI visibility
            self.manageGuiVisibility(False) # Processing done/cancelled!
    
    def cancel_manually(self):
        """ Wrapper of cancel() method,
        used for manual cancellations """
        self.cancel(manualCancel=True)

    def cancel(self, manualCancel=False):
        # Make loop break in LTTL/SegmenterThread.py 
        self.cancel_operation = True

        # Cancel current task
        if self._task is not None:
            self._task.cancel()
            assert self._task.future.done()
            
            # Disconnect slot
            self._task.watcher.done.disconnect(self._task_finished)
            self._task = None
            
            # Send None to output 
            self.send('Merged data', None) # AS 10.2023: removed self

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
            self.optionsBox.setDisabled(1) # Options box: DISABLED

        # Thread done or not running, unfreeze the GUI
        else:
            # If "Send automatically" is disabled, reactivate "Send" button
            if not self.sendButton.autoSendCheckbox.isChecked():
                self.sendButton.mainButton.setDisabled(0) # Send: ENABLED
            # Other buttons and layout
            self.sendButton.cancelButton.setDisabled(1) # Cancel: DISABLED
            self.sendButton.autoSendCheckbox.setDisabled(0) # Send automatically: DISABLED
            self.optionsBox.setDisabled(0) # Options box: ENABLED
            self.cancel_operation = False # Restore to default
            self.signal_prog.emit(100, False) # 100% and do not re-init
            self.sendButton.resetSettingsChangedFlag()
            self.updateGUI()

    def sendData(self):
        """Check inputs, build merged segmentation, then send it"""

        # Check that there's something on input...
        if not self.texts:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Merged data', None) # AS 10.2023: removed self
            return

        # TODO: remove message 'No label was provided.' from docs

        # Extract segmentations from self.texts and get number of segments...
        segmentations = [text[1] for text in self.texts]

        # Check that labelKey is not empty (if necessary)...
        if self.importLabels:
            if self.labelKey:
                labelKey = self.labelKey
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for imported labels.',
                    'warning'
                )
                self.send('Merged data', None) # AS 10.2023: removed self
                return
        else:
            labelKey = None

        # Check that autoNumberKey is not empty (if necessary)...
        if self.autoNumber:
            if self.autoNumberKey:
                autoNumberKey = self.autoNumberKey
            else:
                self.infoBox.setText(
                    u'Please enter an annotation key for auto-numbering.',
                    'warning'
                )
                self.send('Merged data', None) # AS 10.2023: removed self
                return
        else:
            autoNumberKey = None
            
        # Infobox and progress bar
        if self.autoNumber:
            self.infoBox.setText(f"Step 1/2: Processing...", "warning")
        else:
            self.infoBox.setText(u"Processing...", "warning")

        self.progressBarInit()
            
        # Threading ...
        
        # Cancel old tasks
        if self._task is not None:
            self.cancel()
        assert self._task is None

        self._task = task = Task()

        # Perform concatenation.
        threaded_function = partial(
            Segmenter.concatenate,
            caller=self,
            segmentations=segmentations,
            label=self.captionTitle,
            copy_annotations=self.copyAnnotations,
            import_labels_as=labelKey,
            sort=True,  # TODO: document
            auto_number_as=autoNumberKey,
            merge_duplicates=self.mergeDuplicates,
        )
        
        # Restore to default
        self.cancel_operation = False
        
        # Threading start, future, and watcher
        task.future = self._executor.submit(threaded_function)
        task.watcher = FutureWatcher(task.future)
        task.watcher.done.connect(self._task_finished)
        
        # Manage GUI visibility
        self.manageGuiVisibility(True) # Processing
        
    # AS 09.2023
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

    # AS 10.2023
    @pyqtSlot(str, str)
    def update_infobox(self, text, infotype):
        """ Update info box in a thread-safe manner """
        self.infoBox.setText(text, infotype)

    def inputData(self, newItem, newId=None):
        """Process incoming data."""
        # Cancel pending tasks, if any
        self.cancel()
        
        updateMultipleInputs(self.texts, newItem, newId)
        self.textLabels = [text[1].label for text in self.texts]
        self.infoBox.inputChanged()

    def updateGUI(self):
        """Update GUI state"""
        if self.importLabels:
            self.labelKeyLineEdit.setDisabled(False)
        else:
            self.labelKeyLineEdit.setDisabled(True)
        if self.autoNumber:
            self.autoNumberKeyLineEdit.setDisabled(False)
        else:
            self.autoNumberKeyLineEdit.setDisabled(True)

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.cancel() # Cancel current operation
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def handleNewSignals(self):
        """Overridden: called after multiple signals have been added"""
        self.updateGUI()
        self.sendButton.sendIf()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from LTTL.Input import Input

    appl = QApplication(sys.argv)
    ow = OWTextableMerge()
    seg1 = Input(u'hello world', label=u'text1')
    seg2 = Input(u'cruel world', label=u'text2')
    seg3 = Segmenter.concatenate([seg1, seg2], label=u'corpus')
    seg4 = Segmenter.tokenize(seg3,
                              [(r'\w+(?u)', u'tokenize', {'type': 'mot'})],
                              label=u'words')
    ow.inputData(seg3, 1)
    ow.inputData(seg4, 2)
    ow.show()
    appl.exec_()
    ow.saveSettings()
