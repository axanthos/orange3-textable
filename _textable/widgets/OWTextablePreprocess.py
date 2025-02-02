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

__version__ = '0.11.5'


import LTTL.SegmenterThread as Segmenter
from LTTL.Segmentation import Segmentation

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler,
    InfoBox, SendButton, pluralize,
)

from Orange.widgets import gui, settings

# Threading
from functools import partial

class OWTextablePreprocess(OWTextableBaseWidget, openclass=True):
    """Orange widget for standard text preprocessing"""

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
        self.optionsBox = self.create_widgetbox(
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

        # Send button and Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
        self.adjustSizeWithTimer()

    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Data outputs of Segment.Recode
        preprocessed_data = f.result()[0]
        
        # Data treatment
        newNumInputs = len(Segmentation.data)
        self.createdInputIndices = range(self.previousNumInputs, newNumInputs)
        message = u'%i segment@p sent to output.' % len(preprocessed_data)
        message = pluralize(message, len(preprocessed_data))
        self.infoBox.setText(message)
        # caller.signal_text.emit(message, ‘warning’)
        self.send('Preprocessed data', preprocessed_data) # AS 10.2023: removed self
 
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
        self.threading(threaded_function)
        
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
