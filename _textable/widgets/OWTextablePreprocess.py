"""
Class OWTextablePreprocess
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

__version__ = '0.11.4'


import LTTL.SegmenterThread as Segmenter
from LTTL.Segmentation import Segmentation

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton, pluralize,
    Task
)

from Orange.widgets import gui, settings

# Threading
from AnyQt.QtCore import QThread, pyqtSlot, pyqtSignal
import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextablePreprocess(OWTextableBaseWidget):
    """Orange widget for standard text preprocessing"""
    
    # AS 10.2023
    # Signals
    signal_prog = pyqtSignal((int, bool)) # Progress bar (value, init)
    signal_text = pyqtSignal((str, str))  # Text label (text, infotype)

    name = "Preprocess"
    description = "Basic text preprocessing"
    icon = "icons/Preprocess.png"
    priority = 2001

    inputs = [('Segmentation', Segmentation, "inputData",)]
    outputs = [('Preprocessed data', Segmentation)]

    settingsHandler = VersionedSettingsHandler(
        version=__version__.rsplit(".", 1)[0]
    )

    # Settings...
    copyAnnotations = settings.Setting(True)
    applyCaseTransform = settings.Setting(False)
    caseTransform = settings.Setting('to lower')
    removeAccents = settings.Setting(False)

    want_main_area = False

    def __init__(self, *args, **kwargs):
        """Initialize a Preprocess widget"""
        super().__init__(*args, **kwargs)

        # Other attributes...
        self.createdInputIndices = list()
        self.segmentation = None
        self.infoBox = InfoBox(widget=self.controlArea)
        self.sendButton = SendButton(
            widget=self.controlArea,
            master=self,
            callback=self.sendData,
            cancelCallback=self.cancel_manually, # Manual cancel button
            infoBoxAttribute='infoBox',
            sendIfPreCallback=self.updateGUI,
        )

        # GUI...

        # Options box
        self.optionsBox = gui.widgetBox(
            widget=self.controlArea,
            box=u'Options',
            orientation='vertical',
            addSpace=True,
        )
        self.preprocessingBoxLine1 = gui.widgetBox(
            widget=self.optionsBox,
            orientation='horizontal',
        )
        gui.checkBox(
            widget=self.preprocessingBoxLine1,
            master=self,
            value='applyCaseTransform',
            label=u'Transform case:',
            labelWidth=180,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Apply systematic case conversion."
            ),
        )
        self.caseTransformCombo = gui.comboBox(
            widget=self.preprocessingBoxLine1,
            master=self,
            value='caseTransform',
            items=[u'to lower', u'to upper'],
            sendSelectedValue=True,
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Case conversion mode: to lowercase or uppercase."
            ),
        )
        self.caseTransformCombo.setMinimumWidth(120)
        gui.separator(widget=self.optionsBox, height=3)
        gui.checkBox(
            widget=self.optionsBox,
            master=self,
            value='removeAccents',
            label=u'Remove accents',
            callback=self.sendButton.settingsChanged,
            tooltip=(
                u"Replace accented characters with non-accented ones."
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
        gui.separator(widget=self.optionsBox, height=2)

        gui.rubber(self.controlArea)
        
        # Threading
        self._task = None  # type: Optional[Task]
        self._executor = ThreadExecutor()
        self.cancel_operation = False

        # Send button and Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()
        
        # Connect signals to slots
        self.signal_text.connect(self.update_infobox)
        self.signal_prog.connect(self.update_progress_bar)
    
    @pyqtSlot(concurrent.futures.Future)
    def _task_finished(self, f):
        assert self.thread() is QThread.currentThread()
        assert self._task is not None
        assert self._task.future is f
        assert f.done()

        self._task = None
        
        try:
            # Data outputs of Segment.Recode
            preprocessed_data = f.result()[0]
            
            # Data treatment
            newNumInputs = len(Segmentation.data)
            self.createdInputIndices = range(self.previousNumInputs, newNumInputs)
            message = u'%i segment@p sent to output.' % len(preprocessed_data)
            message = pluralize(message, len(preprocessed_data))
            self.infoBox.setText(message)
            self.send('Preprocessed data', preprocessed_data) # AS 10.2023: removed self

        except Exception as ex:
            print(ex)

            # Send None
            self.send('Preprocessed data', None) # AS 10.2023: removed self

        finally:
            # Manage GUI visibility
            self.manageGuiVisibility(False) # Processing done/cancelled
    
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
            self.send('Preprocessed data', None) # AS 10.2023: removed self
            
        if manualCancel:
            self.infoBox.setText(u'Operation cancelled by user.', 'warning')
            
        # Manage GUI visibility
        self.manageGuiVisibility(False) # Processing done/cancelled
        
    def manageGuiVisibility(self, processing=False):
        """ Update GUI and make available (or not) elements
        while the thread task is running in background """

        # Thread currently running, freeze the GUI
        if processing:
            self.optionsBox.setDisabled(1) # Options: DISABLED
            self.sendButton.mainButton.setDisabled(1) # Send button: DISABLED
            self.sendButton.cancelButton.setDisabled(0) # Cancel button: ENABLED
            self.sendButton.autoSendCheckbox.setDisabled(1) # Send automatically: DISABLED

        # Thread done or not running, unfreeze the GUI
        else:
            # If "Send automatically" is disabled, reactivate "Send" button
            if not self.sendButton.autoSendCheckbox.isChecked():
                self.sendButton.mainButton.setDisabled(0) # Send: ENABLED
            # Other buttons and layout
            self.optionsBox.setDisabled(0) # Options: ENABLED
            self.sendButton.cancelButton.setDisabled(1) # Cancel button: DISABLED
            self.sendButton.autoSendCheckbox.setDisabled(0) # Send automatically: ENABLED
            self.cancel_operation = False
            self.signal_prog.emit(100, False) # 100% and do not re-init
            self.sendButton.resetSettingsChangedFlag()
            self.updateGUI()
 
    def inputData(self, newInput):
        """Process incoming data."""
        # Cancel pending tasks, if any
        self.cancel()
        
        self.segmentation = newInput
        self.infoBox.inputChanged()
        self.sendButton.sendIf()

    def sendData(self):
        """Preprocess and send data"""

        if not self.segmentation:
            self.infoBox.setText(u'Widget needs input.', 'warning')
            self.send('Preprocessed data', None) # AS 10.2023: removed self
            return

        if not self.segmentation.is_non_overlapping():
            self.infoBox.setText(
                message=u'Please make sure that input segments are not ' +
                        u'overlapping.',
                state='error'
            )
            self.send('Preprocessed data', None) # AS 10.2023: removed self
            return

        # TODO: remove label message in doc

        if self.applyCaseTransform:
            case = 'lower' if self.caseTransform == 'to lower' else 'upper'
        else:
            case = None
        self.clearCreatedInputIndices()
        self.previousNumInputs = len(Segmentation.data)
        
        # Partial function
        threaded_function = partial(
            Segmenter.recode,
            caller=self,
            segmentation=self.segmentation,
            case=case,
            remove_accents=self.removeAccents,
            label=self.captionTitle,
            copy_annotations=self.copyAnnotations,
            check_overlap=False,
        )
        
        # Infobox and progress bar
        self.infoBox.setText(u'Processing...', 'warning')
        self.progressBarInit()
        
        # Threading ...
        
        # Cancel old tasks
        if self._task is not None:
            self.cancel()
        assert self._task is None

        self._task = task = Task()
        
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
        
    def clearCreatedInputIndices(self):
        for i in self.createdInputIndices:
            Segmentation.set_data(i, None)

    def updateGUI(self):
        """Update GUI state"""
        if self.applyCaseTransform:
            self.caseTransformCombo.setDisabled(False)
        else:
            self.caseTransformCombo.setDisabled(True)

    def setCaption(self, title):
        if 'captionTitle' in dir(self):
            changed = title != self.captionTitle
            super().setCaption(title)
            if changed:
                self.cancel() # Cancel current operation
                self.sendButton.settingsChanged()
        else:
            super().setCaption(title)

    def onDeleteWidget(self):
        self.clearCreatedInputIndices()
        super().onDeleteWidget()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    appl = QApplication(sys.argv)
    ow = OWTextablePreprocess()
    ow.show()
    appl.exec_()
    ow.saveSettings()
