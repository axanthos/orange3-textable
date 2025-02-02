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

__version__ = '0.21.5'


from LTTL.Segmentation import Segmentation
import LTTL.SegmenterThread as Segmenter

from .TextableUtils import (
    OWTextableBaseWidget, VersionedSettingsHandler, ProgressBar,
    updateMultipleInputs, InfoBox, SendButton, pluralize,
    Task
)

from Orange.widgets import widget, gui, settings

# Threading
from Orange.widgets.utils.widgetpreview import WidgetPreview
from functools import partial

class OWTextableMerge(OWTextableBaseWidget):
    """Orange widget for merging segmentations"""

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
        self.optionsBox = self.create_widgetbox(
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

        # Send button & Info box
        self.sendButton.draw()
        self.infoBox.draw()
        self.sendButton.sendIf()
    
    @OWTextableBaseWidget.task_decorator
    def task_finished(self, f):
        # Table outputs
        concatenation = f.result()

        # Send data treatment
        message = u'%i segment@p sent to output.' % len(concatenation)
        message = pluralize(message, len(concatenation))
        self.infoBox.setText(message)
        self.send('Merged data', concatenation) # AS 10.2023: removed self

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
        
        # Threading ...
        self.threading(threaded_function)

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
